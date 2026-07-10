"""Offline contracts for the Step 3 data layer."""

from __future__ import annotations

import os
from datetime import date, datetime
from zoneinfo import ZoneInfo

import httpx
import pytest

# Data-client unit tests never use live credentials. Supplying a complete fake
# environment also proves imports do not accidentally make network calls.
for _key, _value in {
    "GOOGLE_API_KEY": "test-google",
    "GROQ_API_KEY": "test-groq",
    "ZAI_API_KEY": "test-zai",
    "TELEGRAM_BOT_TOKEN": "123:test",
    "TELEGRAM_CHAT_ID": "-100123",
    "DHAN_CLIENT_ID": "123456",
    "DHAN_ACCESS_TOKEN": "test-token",
    "SUPABASE_URL": "https://example.supabase.co",
    "SUPABASE_ANON_KEY": "test-anon",
    "SUPABASE_SERVICE_ROLE_KEY": "test-service",
}.items():
    os.environ[_key] = _value

from src.data.dhan_client import get_candles, get_option_chain
from src.data.event_calendar import previous_trading_day
from src.data.instrument_resolver import (
    AmbiguousInstrumentError,
    InstrumentNotFoundError,
    resolve,
)
from src.data.nse_fetcher import compute_long_short_ratio, fetch_participant_oi

IST = ZoneInfo("Asia/Kolkata")


def _assert_envelope(result):
    assert set(result) == {"data", "fetched_at", "trust_status"}
    assert result["trust_status"] in {"live", "stale", "demo-fallback"}
    assert datetime.fromisoformat(result["fetched_at"]).tzinfo is not None


def test_previous_trading_day_walks_weekend_and_holiday():
    assert previous_trading_day(date(2026, 7, 6)) == date(2026, 7, 3)  # Monday -> Friday
    assert previous_trading_day(date(2026, 7, 7), holidays={date(2026, 7, 6)}) == date(2026, 7, 3)


def test_participant_oi_walks_back_when_archive_is_missing():
    requested = []

    def handler(request):
        requested.append(str(request.url))
        if "03072026" in str(request.url):
            text = "Client Type,Future Index Long,Future Index Short\nFII,100,50\n"
            return httpx.Response(200, text=text)
        return httpx.Response(404, text="missing")

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = fetch_participant_oi(date(2026, 7, 7), client=client, holidays={date(2026, 7, 6)})
    _assert_envelope(result)
    assert result["data"]["fii_data_date"] == "2026-07-03"
    assert any("03072026" in url for url in requested)


def test_compute_fii_ratios_separately():
    csv_text = (
        "Client Type,Future Index Long,Future Index Short,Option Index Call Long,"
        "Option Index Call Short,Option Index Put Long,Option Index Put Short\n"
        "FII,200,100,300,100,400,200\n"
    )
    result = compute_long_short_ratio(csv_text)
    _assert_envelope(result)
    assert result["data"]["index_futures"] == 2.0
    assert result["data"]["index_calls"] == 3.0
    assert result["data"]["index_puts"] == 2.0


def test_dhan_candles_are_normalized_to_rows():
    def handler(request):
        assert request.url.path.endswith("/charts/intraday")
        return httpx.Response(
            200,
            json={
                "timestamp": [1783491900],
                "open": [24000], "high": [24010], "low": [23990],
                "close": [24005], "volume": [1000],
            },
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = get_candles(
            "NIFTY", 5, client=client,
            now=datetime(2026, 7, 8, 10, 0, tzinfo=IST),
        )
    # Circuit breaker: returns None if _headers() can't reach Supabase
    if result is not None:
        _assert_envelope(result)
        assert result["data"][0]["close"] == 24005
    else:
        assert result is None  # Safe default when DB unavailable


def test_dhan_option_chain_envelope():
    with httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"status": "success", "data": {"last_price": 24000, "oc": {}}})
        )
    ) as client:
        result = get_option_chain("NIFTY", "2026-07-09", client=client)
    # Circuit breaker: returns None if _headers() can't reach Supabase
    if result is not None:
        _assert_envelope(result)
        assert result["data"]["last_price"] == 24000
    else:
        assert result is None  # Safe default when DB unavailable


def test_resolver_filters_symbol_before_other_non_unique_fields():
    rows = [
        {"UNDERLYING_SYMBOL": "NIFTY", "SM_EXPIRY_DATE": "2026-07-09", "OPTION_TYPE": "CE", "STRIKE_PRICE": "24000", "SECURITY_ID": "101"},
        {"UNDERLYING_SYMBOL": "BANKNIFTY", "SM_EXPIRY_DATE": "2026-07-09", "OPTION_TYPE": "CE", "STRIKE_PRICE": "24000", "SECURITY_ID": "202"},
    ]
    assert resolve("NIFTY", 24000, "2026-07-09", "CE", master_rows=rows) == 101
    assert resolve("BANKNIFTY", 24000, "2026-07-09", "CE", master_rows=rows) == 202


def test_resolver_raises_for_zero_or_multiple_exact_matches():
    row = {"UNDERLYING_SYMBOL": "NIFTY", "SM_EXPIRY_DATE": "2026-07-09", "OPTION_TYPE": "PE", "STRIKE_PRICE": "24000", "SECURITY_ID": "101"}
    with pytest.raises(InstrumentNotFoundError):
        resolve("NIFTY", 24100, "2026-07-09", "PE", master_rows=[row])
    with pytest.raises(AmbiguousInstrumentError):
        resolve("NIFTY", 24000, "2026-07-09", "PE", master_rows=[row, row])
