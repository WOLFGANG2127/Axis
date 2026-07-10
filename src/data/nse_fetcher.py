"""Read-only NSE option-chain and participant-OI fetchers."""

from __future__ import annotations

import csv
import io
from datetime import date, datetime
from typing import Any, Literal
from zoneinfo import ZoneInfo

import httpx

from src.data.event_calendar import previous_trading_day

IST = ZoneInfo("Asia/Kolkata")
NSE_HOME = "https://www.nseindia.com"
NSE_OPTION_CHAIN = f"{NSE_HOME}/api/option-chain-indices"
NSE_PARTICIPANT_OI = "https://archives.nseindia.com/content/nsccl/fao_participant_oi_{stamp}.csv"
TrustStatus = Literal["live", "stale", "demo-fallback"]
_HEADERS = {
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": f"{NSE_HOME}/option-chain",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AXIS/1.0",
}


def _now() -> datetime:
    return datetime.now(IST)


def _envelope(data: Any, trust_status: TrustStatus = "live") -> dict[str, Any]:
    return {
        "data": data,
        "fetched_at": _now().isoformat(),
        "trust_status": trust_status,
    }


def fetch_option_chain(
    symbol: str,
    *,
    client: httpx.Client | None = None,
) -> dict[str, Any]:
    """Warm an NSE session and fetch an index option-chain snapshot."""
    normalized = symbol.strip().upper()
    if normalized not in {"NIFTY", "BANKNIFTY"}:
        raise ValueError("symbol must be NIFTY or BANKNIFTY")
    owns_client = client is None
    active_client = client or httpx.Client(headers=_HEADERS, timeout=20.0, follow_redirects=True)
    try:
        active_client.get(f"{NSE_HOME}/option-chain").raise_for_status()
        response = active_client.get(NSE_OPTION_CHAIN, params={"symbol": normalized})
        if response.status_code == 200:
            payload = response.json()
            if payload.get("records"):
                return _envelope(payload)
        # NSE retired/disabled its legacy JSON route in some regions in 2026.
        # Dhan is the authenticated, read-only live fallback already authorized
        # by this project; preserve source metadata so quality checks can see it.
        from src.data.dhan_client import get_expiry_list, get_option_chain

        expiries = get_expiry_list(normalized)
        # Circuit-breaker safe: Dhan may return None if tripped
        if expiries is None or not expiries.get("data"):
            return _envelope(
                {"source": "offline", "records": None},
                "stale",
            )
        expiry = expiries["data"][0]
        chain = get_option_chain(normalized, expiry)
        if chain is None:
            return _envelope(
                {"source": "dhan-fallback-offline", "records": None},
                "stale",
            )
        return _envelope(
            {"source": "dhan-fallback", "expiry": expiry, **chain["data"]},
            chain["trust_status"],
        )
    finally:
        if owns_client:
            active_client.close()


def fetch_participant_oi(
    reference_date: date,
    *,
    client: httpx.Client | None = None,
    holidays: set[date] | None = None,
    max_lookback: int = 10,
) -> dict[str, Any]:
    """Fetch the latest prior trading day's CSV, walking past holidays.

    A missing archive on an exchange holiday is treated as another signal to
    walk backward, which protects Monday/pre-market runs from the T+1 trap.
    """
    owns_client = client is None
    active_client = client or httpx.Client(headers=_HEADERS, timeout=20.0, follow_redirects=True)
    candidate = previous_trading_day(reference_date, holidays=holidays)
    attempts = 0
    try:
        while attempts < max_lookback:
            url = NSE_PARTICIPANT_OI.format(stamp=candidate.strftime("%d%m%Y"))
            response = active_client.get(url)
            if response.status_code == 200 and "Client Type" in response.text:
                return _envelope({"csv_text": response.text, "fii_data_date": candidate.isoformat()})
            candidate = previous_trading_day(candidate, holidays=holidays)
            attempts += 1
        raise RuntimeError(f"participant OI unavailable after {max_lookback} trading-day attempts")
    finally:
        if owns_client:
            active_client.close()


def _number(row: dict[str, str], *names: str) -> float:
    normalized = {key.strip().lower(): value for key, value in row.items() if key}
    for name in names:
        value = normalized.get(name.lower())
        if value is not None:
            return float(value.replace(",", "").strip() or 0)
    return 0.0


def _ratio(long_value: float, short_value: float) -> float:
    return float("inf") if short_value == 0 else long_value / short_value


def compute_long_short_ratio(csv_text: str) -> dict[str, Any]:
    """Compute FII futures/calls/puts ratios separately from NSE CSV text."""
    cleaned = csv_text.lstrip("\ufeff").strip()
    rows = list(csv.DictReader(io.StringIO(cleaned)))
    fii = next(
        (row for row in rows if (row.get("Client Type") or row.get("client type") or "").strip().upper() == "FII"),
        None,
    )
    if fii is None:
        raise ValueError("participant OI CSV contains no FII row")
    futures_long = _number(fii, "Future Index Long")
    futures_short = _number(fii, "Future Index Short")
    calls_long = _number(fii, "Option Index Call Long")
    calls_short = _number(fii, "Option Index Call Short")
    puts_long = _number(fii, "Option Index Put Long")
    puts_short = _number(fii, "Option Index Put Short")
    return _envelope(
        {
            "index_futures": _ratio(futures_long, futures_short),
            "index_calls": _ratio(calls_long, calls_short),
            "index_puts": _ratio(puts_long, puts_short),
            "raw": {
                "futures_long": futures_long,
                "futures_short": futures_short,
                "calls_long": calls_long,
                "calls_short": calls_short,
                "puts_long": puts_long,
                "puts_short": puts_short,
            },
        }
    )
