"""Step 6 state, node-contract, and graph-route tests."""

from __future__ import annotations

import asyncio
import inspect
from datetime import datetime
from zoneinfo import ZoneInfo

from src.graph.graph import build_graph
from src.graph import nodes
from src.graph.state import AxisState

IST = ZoneInfo("Asia/Kolkata")


def test_every_axis_state_field_is_optional_and_defaults_none():
    state = AxisState()
    assert all(value is None for value in state.model_dump().values())
    assert all(field.default is None and not field.is_required() for field in AxisState.model_fields.values())


def test_every_graph_node_is_async():
    names = [
        "calendar_gate_node",
        "lock_acquire_node",
        "data_verification_node",
        "direction_scorer_node",
        "structure_gate_node",
        "strategy_activation_node",
        "analyst_node",
        "verifier_node",
        "risk_check_node",
        "dedup_node",
        "telegram_dispatch_node",
    ]
    assert all(inspect.iscoroutinefunction(getattr(nodes, name)) for name in names)


def test_verifier_synthetic_blocks_empty_or_degraded_analyst():
    empty = asyncio.run(
        nodes.verifier_node(AxisState(analyst_opinion=None, degraded_mode=False))
    )
    degraded = asyncio.run(
        nodes.verifier_node(
            AxisState(analyst_opinion={"view": "bearish"}, degraded_mode=True)
        )
    )
    assert empty["verifier_verdict"]["decision"] == "BLOCK"
    assert empty["verifier_verdict"]["synthetic"] is True
    assert degraded["verifier_verdict"]["reason"] == "DEGRADED_DATA"


def test_block_route_ends_before_risk_dedup_and_telegram():
    calls = []

    async def analyst(_state):
        return {"view": "bearish"}

    async def verifier(_state):
        return {"decision": "BLOCK"}

    async def risk(_state):
        calls.append("risk")
        return True

    nodes.configure_node_services(analyst=analyst, verifier=verifier, risk_check=risk)
    try:
        result = asyncio.run(
            build_graph().ainvoke(
                {
                    "symbol": "NIFTY",
                    "cycle_timestamp": datetime.now(IST),
                    "market_context": {
                        "direction_score": 1,
                        "structure_confirmed": False,
                    },
                }
            )
        )
    finally:
        nodes.reset_node_services()
    assert result["verifier_verdict"]["decision"] == "BLOCK"
    assert calls == []
    assert result.get("risk_approved") is None


def test_proceed_route_runs_risk_then_dedup_then_telegram():
    calls = []

    async def analyst(_state):
        calls.append("analyst")
        return {"view": "bearish"}

    async def verifier(_state):
        calls.append("verifier")
        return {"decision": "PROCEED"}

    async def risk(_state):
        calls.append("risk")
        return True

    async def dedup(_state):
        calls.append("dedup")
        return False

    async def telegram(_state):
        calls.append("telegram")
        return True

    nodes.configure_node_services(
        analyst=analyst,
        verifier=verifier,
        risk_check=risk,
        dedup_check=dedup,
        telegram_send=telegram,
    )
    try:
        result = asyncio.run(
            build_graph().ainvoke(
                {
                    "symbol": "NIFTY",
                    "cycle_timestamp": datetime.now(IST),
                    "market_context": {
                        "direction_score": 1,
                        "structure_confirmed": False,
                    },
                }
            )
        )
    finally:
        nodes.reset_node_services()
    assert calls == ["analyst", "verifier", "risk", "dedup", "telegram"]
    assert result["risk_approved"] is True
    assert result["dedup_status"] == "CLEAR"
    assert result["alert_sent"] is True
