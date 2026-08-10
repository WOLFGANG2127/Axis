"""D-007: OHLC candle persistence.

Upserts candle data into the ``ohlc_candles`` table.
Conflict key: ``(symbol, interval, timestamp)`` — do nothing, idempotent.

Public API
----------
candle_rows_from_context(symbol, interval, cycle_timestamp, correlation_id, candles) -> list[dict]
    Normalise the candles envelope from market_context into upsert-ready rows.

persist_ohlc_candles(*, symbol, interval, candles, db=None, cycle_timestamp=None, correlation_id=None) -> int
    Persist normalised rows.  Returns number of rows attempted.
    If ``db`` is None, obtains the live Supabase client via get_supabase_client().
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

_log = logging.getLogger("axis.ohlc_writer")

_TABLE = "ohlc_candles"
_CONFLICT_KEY = "symbol,interval,timestamp"


# ---------------------------------------------------------------------------
# Public helper — extracted so tests can verify normalisation independently
# ---------------------------------------------------------------------------

def candle_rows_from_context(
    *,
    symbol: str,
    interval: str,
    cycle_timestamp: datetime | str | None,
    correlation_id: str | None,
    candles: Any,
) -> list[dict[str, Any]]:
    """Convert a candle envelope dict (or bare list) into upsert-ready rows.

    The envelope format coming from ``dhan_client`` / ``market_snapshot``::

        {
            "trust_status": "live",
            "fetched_at": "2026-07-14T10:00:02+05:30",
            "data": [ {"timestamp": ..., "open": ..., ...}, ... ]
        }

    A bare list of candle dicts is also accepted for backward-compatibility.
    """
    # Resolve envelope vs bare list
    if isinstance(candles, dict):
        envelope_meta = {
            "trust_status": candles.get("trust_status"),
            "fetched_at": candles.get("fetched_at"),
        }
        raw_list: list[Any] = candles.get("data") or []
    elif isinstance(candles, (list, tuple)):
        envelope_meta = {}
        raw_list = list(candles)
    else:
        return []

    # Serialise cycle_timestamp to ISO string once
    if isinstance(cycle_timestamp, datetime):
        cycle_ts_str: str | None = cycle_timestamp.isoformat()
    else:
        cycle_ts_str = str(cycle_timestamp) if cycle_timestamp is not None else None

    rows: list[dict[str, Any]] = []
    for raw in raw_list:
        if not isinstance(raw, dict):
            continue
        ts = raw.get("timestamp")
        if ts is None:
            continue
        if isinstance(ts, datetime):
            ts = ts.isoformat()
        else:
            ts = str(ts)

        def _float(v: Any) -> float | None:
            if v is None:
                return None
            try:
                return float(v)
            except (TypeError, ValueError):
                return None

        row: dict[str, Any] = {
            "symbol": symbol,
            "interval": interval,
            "timestamp": ts,
            "open": _float(raw.get("open")),
            "high": _float(raw.get("high")),
            "low": _float(raw.get("low")),
            "close": _float(raw.get("close")),
            "volume": _float(raw.get("volume")),
            "oi": _float(raw.get("oi")),
            "source": "dhan",
            "cycle_timestamp": cycle_ts_str,
            "correlation_id": correlation_id,
        }
        # Merge envelope metadata (trust_status, fetched_at) into row
        for k, v in envelope_meta.items():
            if v is not None:
                row[k] = v
        rows.append(row)

    return rows


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def persist_ohlc_candles(
    *,
    symbol: str,
    candles: Any,
    interval: str = "5",
    db: Any = None,
    cycle_timestamp: datetime | str | None = None,
    correlation_id: str | None = None,
) -> int:
    """Upsert candle rows into ``ohlc_candles``.

    Args:
        symbol: Instrument identifier (e.g. ``"NIFTY"``).
        candles: Envelope dict with ``{"data": [...]}`` or bare list of
            candle dicts from ``dhan_client.fetch_candles()``.
            ``None`` or empty → silent no-op, returns 0.
        interval: Candle interval in minutes as string (default ``"5"``).
        db: Optional Supabase client; if ``None`` uses the live
            ``get_supabase_client()`` singleton.
        cycle_timestamp: Pipeline cycle timestamp; embedded in each row for
            auditability.
        correlation_id: Pipeline correlation ID; embedded in each row.

    Returns:
        Number of rows passed to the upsert call (0 on no-op).
    """
    if not candles:
        return 0

    rows = candle_rows_from_context(
        symbol=symbol,
        interval=interval,
        cycle_timestamp=cycle_timestamp,
        correlation_id=correlation_id,
        candles=candles,
    )

    if not rows:
        _log.warning(
            "persist_ohlc_candles: no valid rows for %s interval=%s "
            "(correlation_id=%s)",
            symbol,
            interval,
            correlation_id,
        )
        return 0

    if db is None:
        from src.database.supabase import get_supabase_client
        db = get_supabase_client()

    db.table(_TABLE).upsert(rows, on_conflict=_CONFLICT_KEY).execute()

    _log.debug(
        "persist_ohlc_candles: upserted %d rows for %s interval=%s "
        "(cycle_timestamp=%s, correlation_id=%s)",
        len(rows),
        symbol,
        interval,
        cycle_timestamp,
        correlation_id,
    )
    return len(rows)
