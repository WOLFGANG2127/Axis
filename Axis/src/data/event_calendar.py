"""IST-aware market-event and previous-trading-day helpers."""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from typing import Iterable
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


def _as_date(value: date | datetime | str) -> date:
    if isinstance(value, datetime):
        return value.astimezone(IST).date() if value.tzinfo else value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def _environment_dates(name: str) -> set[date]:
    raw = os.environ.get(name, "")
    return {date.fromisoformat(item.strip()) for item in raw.split(",") if item.strip()}


def get_monthly_expiries() -> set[date]:
    """Return the set of monthly expiry dates configured in the environment."""
    return _environment_dates("AXIS_MONTHLY_EXPIRIES")


def previous_trading_day(
    reference_date: date | datetime,
    *,
    holidays: Iterable[date | str] | None = None,
) -> date:
    """Walk backward over weekends and configured exchange holidays."""
    holiday_dates = (
        {_as_date(item) for item in holidays}
        if holidays is not None
        else _environment_dates("AXIS_MARKET_HOLIDAYS")
    )
    candidate = _as_date(reference_date) - timedelta(days=1)
    while candidate.weekday() >= 5 or candidate in holiday_dates:
        candidate -= timedelta(days=1)
    return candidate


def days_to_next_event(
    reference: date | datetime | None = None,
    *,
    events: Iterable[date | str] | None = None,
) -> int | None:
    """Return calendar days to the next configured macro/expiry event."""
    today = _as_date(reference or datetime.now(IST))
    event_dates = (
        {_as_date(item) for item in events}
        if events is not None
        else _environment_dates("AXIS_EVENT_DATES")
    )
    future = [event_date for event_date in event_dates if event_date >= today]
    return min((event_date - today).days for event_date in future) if future else None


def is_event_proximity_window(
    reference: date | datetime | None = None,
    *,
    events: Iterable[date | str] | None = None,
    window_days: int = 1,
) -> bool:
    """Return whether the next event is within the configured stop window."""
    if window_days < 0:
        raise ValueError("window_days cannot be negative")
    days = days_to_next_event(reference, events=events)
    return days is not None and days <= window_days

