"""Persist already-fetched OHLC candles for charting.

This module is intentionally write-only and source-agnostic. It does not fetch
market data; it only relays candle rows that the AXIS cycle already has in
AxisState.market_context.
"""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Mapping
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
VALID_SYMBOLS = {"NIFTY", "BANKNIFTY"}
logger = logging.getLogger("axis.ohlc")


def _payload(value: Any) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if isinstance(value, Mapping):
        data = value.get("data", [])
        return list(data or []) if isinstance(data, Iterable) and not isinstance(data, (str, bytes, Mapping)) else []
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, Mapping)):
        return list(value)
    return []


def _trust_status(value: Any, default: str = "live") -> str:
    if isinstance(value, Mapping):
        status = str(value.get("trust_status") or default)
        return status if status in {"live", "stale", "demo-fallback"} else default
    return default


def _fetched_at(value: Any) -> str | None:
    if isinstance(value, Mapping) and value.get("fetched_at"):
        return _timestamp(value["fetched_at"])
    return None


def _number(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(Decimal(str(value)))
    except (InvalidOperation, ValueError):
        return None


def _timestamp(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=IST)
    return parsed.astimezone(IST).isoformat()


def candle_rows_from_context(
    *,
    symbol: str,
    candles: Any,
    interval: str = "5",
    cycle_timestamp: datetime | str | None = None,
    correlation_id: str | None = None,
    source: str = "dhan",
) -> list[dict[str, Any]]:
    """Normalize candle payloads into ohlc_candles upsert rows."""

    normalized_symbol = symbol.strip().upper()
    if normalized_symbol not in VALID_SYMBOLS:
        raise ValueError("symbol must be NIFTY or BANKNIFTY")
    trust_status = _trust_status(candles)
    fetched_at = _fetched_at(candles)
    cycle_ts = _timestamp(cycle_timestamp)

    rows: list[dict[str, Any]] = []
    for candle in _payload(candles):
        if not isinstance(candle, Mapping):
            continue
        stamp = _timestamp(candle.get("timestamp") or candle.get("time"))
        open_ = _number(candle.get("open"))
        high = _number(candle.get("high"))
        low = _number(candle.get("low"))
        close = _number(candle.get("close"))
        if stamp is None or None in (open_, high, low, close):
            continue
        rows.append(
            {
                "symbol": normalized_symbol,
                "interval": str(candle.get("interval") or interval),
                "timestamp": stamp,
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": _number(candle.get("volume")),
                "oi": _number(candle.get("oi")),
                "source": source,
                "trust_status": trust_status,
                "fetched_at": fetched_at,
                "cycle_timestamp": cycle_ts,
                "correlation_id": correlation_id,
            }
        )
    return rows


def persist_ohlc_candles(
    *,
    symbol: str,
    candles: Any,
    db: Any | None = None,
    interval: str = "5",
    cycle_timestamp: datetime | str | None = None,
    correlation_id: str | None = None,
    source: str = "dhan",
) -> int:
    """Upsert already-fetched candle rows and return the persisted row count."""

    rows = candle_rows_from_context(
        symbol=symbol,
        candles=candles,
        interval=interval,
        cycle_timestamp=cycle_timestamp,
        correlation_id=correlation_id,
        source=source,
    )
    if not rows:
        return 0
    database = db
    if database is None:
        from src.database.supabase import get_supabase_client

        database = get_supabase_client()
    try:
        database.table("ohlc_candles").upsert(rows, on_conflict="symbol,interval,timestamp").execute()
        return len(rows)
    except Exception as exc:
        logger.error("Failed to persist OHLC candles for %s: %s", symbol, exc)
        return 0

