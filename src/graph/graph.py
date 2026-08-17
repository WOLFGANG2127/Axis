"""Exact Step 6 LangGraph wiring for AXIS."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from src.graph.nodes import (
    analyst_node,
    calendar_gate_node,
    data_verification_node,
    dedup_node,
    direction_scorer_node,
    lock_acquire_node,
    risk_check_node,
    strategy_activation_node,
    structure_gate_node,
    telegram_dispatch_node,
    verifier_node,
    verifier_route,
)
from src.graph.state import AxisState


def build_graph():
    builder = StateGraph(AxisState)
    builder.add_node("calendar_gate", calendar_gate_node)
    builder.add_node("lock_acquire", lock_acquire_node)
    builder.add_node("data_verification", data_verification_node)
    builder.add_node("direction_scorer", direction_scorer_node)
    builder.add_node("structure_gate", structure_gate_node)
    builder.add_node("strategy_activation", strategy_activation_node)
    builder.add_node("analyst_node", analyst_node)
    builder.add_node("verifier_node", verifier_node)
    builder.add_node("risk", risk_check_node)
    builder.add_node("dedup", dedup_node)
    builder.add_node("telegram", telegram_dispatch_node)

    builder.add_edge(START, "calendar_gate")
    builder.add_edge("calendar_gate", "lock_acquire")
    builder.add_edge("lock_acquire", "data_verification")
    builder.add_edge("data_verification", "direction_scorer")
    builder.add_edge("direction_scorer", "structure_gate")
    builder.add_edge("structure_gate", "strategy_activation")
    builder.add_edge("strategy_activation", "analyst_node")
    builder.add_edge("analyst_node", "verifier_node")
    builder.add_conditional_edges(
        "verifier_node",
        verifier_route,
        {"BLOCK": END, "PROCEED": "risk"},
    )
    builder.add_edge("risk", "dedup")
    builder.add_edge("dedup", "telegram")
    builder.add_edge("telegram", END)
    return builder.compile()


graph = build_graph()
