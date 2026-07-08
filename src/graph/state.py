"""Pydantic state contract shared by every AXIS graph node."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class AxisState(BaseModel):
    """One immutable-looking snapshot of a single symbol analysis cycle.

    Every field is optional by design: LangGraph constructs the state before
    downstream nodes have populated their outputs.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    symbol: Optional[str] = None
    is_backtest: Optional[bool] = None
    cycle_timestamp: Optional[datetime] = None
    market_context: Optional[dict[str, Any]] = None
    calendar_open: Optional[bool] = None
    lock_acquired: Optional[bool] = None
    data_quality: Optional[dict[str, Any]] = None
    direction_score: Optional[int] = None
    structure_confirmed: Optional[bool] = None
    active_strategy: Optional[dict[str, Any]] = None
    analyst_opinion: Optional[dict[str, Any] | str] = None
    verifier_verdict: Optional[dict[str, Any] | str] = None
    degraded_mode: Optional[bool] = None
    risk_approved: Optional[bool] = None
    dedup_status: Optional[str] = None
    alert_sent: Optional[bool] = None
    correlation_id: Optional[str] = None
    node_error: Optional[dict[str, Any]] = None
