"""Governance gate-mode policy for strategy activation and manual promotion."""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
MIN_SHADOW_OBSERVATION_DAYS = 3
MIN_SIGNAL_SAMPLE_FLOOR = 15
GOVERNANCE_GATES = (
    "DAILY_LOSS_BREAKER",
    "RR_FILTER",
    "CROSS_SYMBOL_CORRELATION",
)


def new_strategy_gate_modes() -> dict[str, str]:
    """Return mandatory SHADOW modes for every newly activated strategy gate."""
    return {gate: "SHADOW" for gate in GOVERNANCE_GATES}


def shadow_observation_complete(shadow_started_at: datetime, *, now: datetime | None = None, min_days: int = MIN_SHADOW_OBSERVATION_DAYS) -> bool:
    """True only after the strategy has spent the minimum time in SHADOW."""
    current = now or datetime.now(IST)
    if shadow_started_at.tzinfo is None:
        shadow_started_at = shadow_started_at.replace(tzinfo=IST)
    return current.astimezone(IST) - shadow_started_at.astimezone(IST) >= timedelta(days=min_days)


def enforce_promotion_eligible(*, shadow_started_at: datetime, signal_sample_count: int, now: datetime | None = None) -> bool:
    """UI eligibility for manual SHADOW -> ENFORCE promotion; never promotes."""
    return shadow_observation_complete(shadow_started_at, now=now) and signal_sample_count >= MIN_SIGNAL_SAMPLE_FLOOR
