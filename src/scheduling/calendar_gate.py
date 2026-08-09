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


def is_system_paused(
    *,
    db: Any | None = None,
    now: datetime | None = None,
) -> tuple[bool, str | None]:
    """Read the single-row ``system_paused`` kill switch and trader_session_state.

    D-052 / D-T8: Strict fail-closed policy. If the table/client is unavailable,
    queries fail, or the system_paused table is empty (0 rows returned), resolve
    to PAUSED (True).
    """

    database = db
    if database is None:
        try:
            from src.scheduling.lock_manager import get_lock_db

            database = get_lock_db()
        except Exception:
            database = None

    if database is None:
        return True, "UNREADABLE_PAUSE_STATE"

    # Step 1: Read system_paused
    try:
        rows = _table_data(database.table("system_paused").select("*").limit(1))
    except Exception as exc:
        return True, f"UNREADABLE_PAUSE_STATE: {exc}"

    if not rows:
        return True, "UNREADABLE_PAUSE_STATE"

    row = rows[0]
    is_paused = row.get("is_paused") if "is_paused" in row else row.get("paused")
    if is_paused is None:
        return True, "UNREADABLE_PAUSE_STATE"
    if bool(is_paused):
        reason = row.get("paused_reason") or row.get("reason") or "Operator paused system"
        return True, str(reason)

    # Step 2: Read trader_session_state readiness
    try:
        today_iso = _as_ist(now).date().isoformat()
        session_rows = _table_data(
            database.table("trader_session_state")
            .select("is_ready")
            .eq("session_date", today_iso)
            .limit(1)
        )
        if not session_rows or not bool(session_rows[0].get("is_ready")):
            return True, "TRADER_SESSION_NOT_READY"
    except Exception:
        return True, "TRADER_SESSION_READ_ERROR"

    return False, None
