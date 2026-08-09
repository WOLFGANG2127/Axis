"""Comprehensive unit tests for Agent 4 Orchestrator tasks (D-005, D-009, D-008, D-049, D-050, D-052)."""

import asyncio
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

import pytest

from main import (
    CYCLE_WALL_CLOCK_TIMEOUT_SECONDS,
    _run_cli,
    _send_pipeline_crash_alert,
    apply_same_cycle_correlation,
    run_all_symbols_cycle,
    run_cycle,
)
from src.graph.nodes import _log, dedup_node, position_state_check_node
from src.graph.state import AxisState
from src.scheduling.calendar_gate import is_system_paused

IST = ZoneInfo("Asia/Kolkata")


# ── D-005: Logger Definition ──────────────────────────────────────────────────
def test_d005_nodes_logger_defined():
    """D-005: _log logger must be defined at module level in nodes.py."""
    assert _log is not None
    assert _log.name == "axis.nodes"


# ── D-052: Fail-Closed Kill Switch ────────────────────────────────────────────
def test_d052_system_paused_fail_closed_on_none_db():
    """D-052: is_system_paused must return True (paused) when db is None."""
    paused, reason = is_system_paused(db=None)
    assert paused is True
    assert "UNREADABLE_PAUSE_STATE" in (reason or "")


def test_d052_system_paused_fail_closed_on_query_exception():
    """D-052: is_system_paused must return True when query raises an exception."""
    mock_db = MagicMock()
    mock_db.table.side_effect = Exception("Supabase connection timeout")

    paused, reason = is_system_paused(db=mock_db)
    assert paused is True
    assert "UNREADABLE_PAUSE_STATE" in (reason or "")


def test_d052_system_paused_fail_closed_on_empty_rows():
    """D-052: is_system_paused must return True when query returns 0 rows."""
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.execute.return_value.data = []
    mock_db.table.return_value.select.return_value.limit.return_value = mock_query

    paused, reason = is_system_paused(db=mock_db)
    assert paused is True
    assert reason == "UNREADABLE_PAUSE_STATE"


def test_d052_system_paused_when_explicitly_true():
    """D-052: is_system_paused returns True when system_paused has is_paused=True."""
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.execute.return_value.data = [{"is_paused": True, "paused_reason": "Operator maintenance"}]
    mock_db.table.return_value.select.return_value.limit.return_value = mock_query

    paused, reason = is_system_paused(db=mock_db)
    assert paused is True
    assert reason == "Operator maintenance"


def test_d052_system_paused_unready_trader_session():
    """D-052: returns True if system_paused is False but trader_session_state is not ready."""
    mock_db = MagicMock()

    def mock_table(name: str):
        builder = MagicMock()
        if name == "system_paused":
            query = MagicMock()
            query.execute.return_value.data = [{"is_paused": False}]
            builder.select.return_value.limit.return_value = query
        elif name == "trader_session_state":
            query = MagicMock()
            query.execute.return_value.data = []  # No row for today
            builder.select.return_value.eq.return_value.limit.return_value = query
        return builder

    mock_db.table.side_effect = mock_table

    paused, reason = is_system_paused(db=mock_db)
    assert paused is True
    assert reason == "TRADER_SESSION_NOT_READY"


def test_d052_system_paused_cleared_when_all_ready():
    """D-052: returns False only when system_paused=False AND trader_session_state is ready."""
    mock_db = MagicMock()

    def mock_table(name: str):
        builder = MagicMock()
        if name == "system_paused":
            query = MagicMock()
            query.execute.return_value.data = [{"is_paused": False}]
            builder.select.return_value.limit.return_value = query
        elif name == "trader_session_state":
            query = MagicMock()
            query.execute.return_value.data = [{"is_ready": True}]
            builder.select.return_value.eq.return_value.limit.return_value = query
        return builder

    mock_db.table.side_effect = mock_table

    paused, reason = is_system_paused(db=mock_db)
    assert paused is False
    assert reason is None


# ── D-050: Active Position Tracking Logic ────────────────────────────────────
@pytest.mark.anyio
async def test_d050_position_state_check_same_direction_suppressed():
    """D-050: Same direction open position suppresses signal."""
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.execute.return_value.data = [{"symbol": "NIFTY", "option_type": "CE", "entry_price": 24000}]
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value = mock_query

    state = AxisState(
        symbol="NIFTY",
        active_strategy={"strategy_name": "GVOF", "direction": "long"},
    )

    with patch("src.database.supabase.get_supabase_client", return_value=mock_db):
        res = await position_state_check_node(state)
        assert res["position_conflict"] is True
        assert res["risk_approved"] is False
        assert res["dedup_status"] == "POSITION_HELD_SUPPRESSED"


@pytest.mark.anyio
async def test_d050_position_state_check_opposite_direction_exit_warning():
    """D-050: Opposite direction open position sets exit warning."""
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.execute.return_value.data = [{"symbol": "NIFTY", "option_type": "PE", "entry_price": 24000}]
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value = mock_query

    state = AxisState(
        symbol="NIFTY",
        active_strategy={"strategy_name": "GVOF", "direction": "long"},
    )

    with patch("src.database.supabase.get_supabase_client", return_value=mock_db):
        res = await position_state_check_node(state)
        assert res["position_conflict"] == "EXIT_WARNING"
        assert res["exit_warning"] is True


@pytest.mark.anyio
async def test_d050_position_state_check_no_position():
    """D-050: No open position returns position_conflict=False."""
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.execute.return_value.data = []
    mock_db.table.return_value.select.return_value.eq.return_value.limit.return_value = mock_query

    state = AxisState(
        symbol="NIFTY",
        active_strategy={"strategy_name": "GVOF", "direction": "long"},
    )

    with patch("src.database.supabase.get_supabase_client", return_value=mock_db):
        res = await position_state_check_node(state)
        assert res["position_conflict"] is False


# ── D-049: 60-Minute Dedup Suppression ───────────────────────────────────────
@pytest.mark.anyio
async def test_d049_dedup_suppresses_identical_recent_signal():
    """D-049: Signal dispatched within 60 min with same (symbol, direction, strategy) is suppressed."""
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.execute.return_value.data = [{"id": "sig-123"}]
    mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.limit.return_value = mock_query

    now = datetime.now(IST)
    state = AxisState(
        symbol="NIFTY",
        cycle_timestamp=now,
        risk_approved=True,
        active_strategy={"strategy_name": "GVOF", "direction": "long"},
    )

    with patch("src.database.supabase.get_supabase_client", return_value=mock_db):
        res = await dedup_node(state)
        assert res["dedup_status"] == "DUPLICATE_SUPPRESSED"


@pytest.mark.anyio
async def test_d049_dedup_allows_signal_when_no_recent_match():
    """D-049: Returns CLEAR when no signal exists within 60 min."""
    mock_db = MagicMock()
    mock_query = MagicMock()
    mock_query.execute.return_value.data = []
    mock_db.table.return_value.select.return_value.eq.return_value.eq.return_value.eq.return_value.gte.return_value.limit.return_value = mock_query

    now = datetime.now(IST)
    state = AxisState(
        symbol="NIFTY",
        cycle_timestamp=now,
        risk_approved=True,
        active_strategy={"strategy_name": "GVOF", "direction": "long"},
    )

    with patch("src.database.supabase.get_supabase_client", return_value=mock_db):
        res = await dedup_node(state)
        assert res["dedup_status"] == "CLEAR"


# ── D-008 & D-009: Orchestrator Correlation & Crash Alerting ─────────────────
def test_d008_apply_same_cycle_correlation_single_location():
    """D-008: apply_same_cycle_correlation applies 50% haircut to same-direction signals."""
    results = [
        {
            "symbol": "NIFTY",
            "candidate_signals": [{"strategy_name": "gvof", "direction": "long", "lots": 4, "capital_deployed": 100000}],
            "verifier_verdicts": {"gvof": {"decision": "PROCEED"}},
        },
        {
            "symbol": "BANKNIFTY",
            "candidate_signals": [{"strategy_name": "gvof", "direction": "long", "lots": 6, "capital_deployed": 150000}],
            "verifier_verdicts": {"gvof": {"decision": "PROCEED"}},
        },
    ]

    correlated = apply_same_cycle_correlation(results)
    assert len(correlated) == 2
    assert correlated[0]["candidate_signals"][0]["lots"] == 2
    assert correlated[1]["candidate_signals"][0]["lots"] == 3
    assert correlated[0]["candidate_signals"][0]["cross_symbol_haircut_applied"] is True


def test_d009_pipeline_crash_alert_sender():
    """D-009: _send_pipeline_crash_alert attempts telegram dispatch on exception."""
    with patch("src.delivery.telegram_formatter.send_telegram_alert") as mock_send:
        _send_pipeline_crash_alert(RuntimeError("Test pipeline crash"))
        mock_send.assert_called_once()
        args = mock_send.call_args[0]
        assert "AXIS PIPELINE CRASHED" in args[2]


def test_d009_run_cli_invokes_amain_and_catches_crash():
    """D-009: _run_cli catches crash and triggers Telegram alert."""
    with patch("main._amain", side_effect=ValueError("Simulated CLI error")), \
         patch("main._send_pipeline_crash_alert") as mock_alert:
        with pytest.raises(ValueError, match="Simulated CLI error"):
            _run_cli()
        mock_alert.assert_called_once()


def test_wall_clock_timeout_constant_configured():
    """Wall-clock timeout guard constant is set under 300s (D-051 timeout)."""
    assert CYCLE_WALL_CLOCK_TIMEOUT_SECONDS < 300.0
    assert CYCLE_WALL_CLOCK_TIMEOUT_SECONDS == 280.0
