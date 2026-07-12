"""Phase 2.5 OHLC candle persistence tests."""

from __future__ import annotations

import asyncio
from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


class FakeOHLCTable:
    def __init__(self, db, name: str):
        self.db = db
        self.name = name

    def upsert(self, payload, **kwargs):
        self.db.upserts.append((self.name, payload, kwargs))
        return self

    def execute(self):
        return SimpleNamespace(data=[])


class FakeOHLCDB:
    def __init__(self):
        self.upserts = []

    def table(self, name: str):
        return FakeOHLCTable(self, name)


def test_ohlc_migration_contract_uses_existing_feed_not_third_party_sources():
    from pathlib import Path

    sql = Path("migrations/021_ohlc_candles.sql").read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS ohlc_candles" in sql
    assert "PRIMARY KEY (symbol, interval, \"timestamp\")" in sql
    assert "TIMESTAMPTZ" in sql
    assert "source           TEXT NOT NULL DEFAULT 'dhan'" in sql
    assert "yahoo" not in sql.lower()
    assert "tradingview" not in sql.lower()


def test_candle_rows_from_context_normalizes_envelope_to_upsert_rows():
    from src.data.ohlc_writer import candle_rows_from_context

    rows = candle_rows_from_context(
        symbol="NIFTY",
        interval="5",
        cycle_timestamp=datetime(2026, 7, 14, 10, 0, tzinfo=IST),
        correlation_id="cid-1",
        candles={
            "trust_status": "live",
            "fetched_at": "2026-07-14T10:00:02+05:30",
            "data": [
                {
                    "timestamp": "2026-07-14T09:15:00+05:30",
                    "open": "24000",
                    "high": 24025,
                    "low": 23990,
                    "close": 24010,
                    "volume": 12345,
                    "oi": None,
                }
            ],
        },
    )

    assert rows == [
        {
            "symbol": "NIFTY",
            "interval": "5",
            "timestamp": "2026-07-14T09:15:00+05:30",
            "open": 24000.0,
            "high": 24025.0,
            "low": 23990.0,
            "close": 24010.0,
            "volume": 12345.0,
            "oi": None,
            "source": "dhan",
            "trust_status": "live",
            "fetched_at": "2026-07-14T10:00:02+05:30",
            "cycle_timestamp": "2026-07-14T10:00:00+05:30",
            "correlation_id": "cid-1",
        }
    ]


def test_persist_ohlc_candles_upserts_symbol_interval_timestamp_key():
    from src.data.ohlc_writer import persist_ohlc_candles

    db = FakeOHLCDB()
    count = persist_ohlc_candles(
        symbol="BANKNIFTY",
        interval="5",
        db=db,
        candles=[
            {
                "timestamp": "2026-07-14T09:15:00+05:30",
                "open": 52000,
                "high": 52100,
                "low": 51950,
                "close": 52050,
            }
        ],
    )

    assert count == 1
    table, payload, kwargs = db.upserts[-1]
    assert table == "ohlc_candles"
    assert kwargs["on_conflict"] == "symbol,interval,timestamp"
    assert payload[0]["symbol"] == "BANKNIFTY"


def test_data_verification_node_persists_existing_candles_without_fetching(monkeypatch):
    from src.graph.nodes import data_verification_node
    from src.graph.state import AxisState

    calls = []

    def fake_persist(**kwargs):
        calls.append(kwargs)
        return 1

    monkeypatch.setattr("src.data.ohlc_writer.persist_ohlc_candles", fake_persist)

    result = asyncio.run(
        data_verification_node(
            AxisState(
                symbol="NIFTY",
                cycle_timestamp=datetime(2026, 7, 14, 10, 0, tzinfo=IST),
                correlation_id="cid-2",
                market_context={
                    "candle_interval": "5",
                    "candles": {
                        "trust_status": "live",
                        "data": [
                            {
                                "timestamp": "2026-07-14T09:15:00+05:30",
                                "open": 1,
                                "high": 2,
                                "low": 1,
                                "close": 2,
                            }
                        ],
                    },
                },
            )
        )
    )

    assert result["degraded_mode"] is False
    assert calls and calls[-1]["symbol"] == "NIFTY"
    assert calls[-1]["candles"]["data"][0]["close"] == 2

