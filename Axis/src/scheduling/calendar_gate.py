"""IST-aware market calendar and system pause gates."""

from __future__ import annotations

import os
from datetime import date, datetime, time
from typing import Any, Iterable
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)


def _as_ist(now: datetime | None = None) -> datetime:
    current = now or datetime.now(IST)
    return current.replace(tzinfo=IST) if current.tzinfo is None else current.astimezone(IST)


def _env_holidays() -> set[date]:
    raw = os.environ.get("AXIS_MARKET_HOLIDAYS", "")
    return {date.fromisoformat(item.strip()) for item in raw.split(",") if item.strip()}


def is_market_open(
    now: datetime | None = None,
    *,
    holidays: Iterable[date | str] | None = None,
) -> bool:
    """Return True only during live NSE index-option market hours."""

    local = _as_ist(now)
    holiday_dates = (
        {date.fromisoformat(item) if isinstance(item, str) else item for item in holidays}
        if holidays is not None
        else _env_holidays()
    )
    if local.weekday() >= 5 or local.date() in holiday_dates:
        return False
    return MARKET_OPEN <= local.time().replace(tzinfo=None) <= MARKET_CLOSE


def _table_data(query: Any) -> list[dict[str, Any]]:
    data = query.execute().data
    return data or []


def is_system_paused(*, db: Any | None = None) -> tuple[bool, str | None]:
    """Read the single-row ``system_paused`` kill switch.

    If the table/client is unavailable, fail open so a missing optional DB
    check does not masquerade as a deliberate operator pause.
    """

    if db is None:
        try:
            from src.scheduling.lock_manager import get_lock_db

            db = get_lock_db()
        except Exception:
            db = None
    if db is None:
        return False, None
    try:
        rows = _table_data(db.table("system_paused").select("paused,reason").limit(1))
    except Exception:
        return False, None
    if not rows:
        return False, None
    row = rows[0]
    return bool(row.get("paused")), row.get("reason")
