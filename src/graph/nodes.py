"""Async, partial-update-only nodes for the AXIS graph."""

from __future__ import annotations

import inspect
from dataclasses import dataclass, fields
from datetime import datetime
from typing import Any, Awaitable, Callable, Mapping
from zoneinfo import ZoneInfo

from src.graph.state import AxisState
from src.scoring.direction_scorer import compute_direction_score
from src.scoring.structure_gate import check_structure
from src.strategies.base import BaseStrategy
from src.strategies.gvof import GVOFStrategy

IST = ZoneInfo("Asia/Kolkata")
Service = Callable[..., Any | Awaitable[Any]]


@dataclass
class NodeServices:
    """Replaceable I/O boundaries; concrete Step 8–10 services plug in here."""

    calendar_check: Service | None = None
    lock_acquire: Service | None = None
    analyst: Service | None = None
    verifier: Service | None = None
    risk_check: Service | None = None
    dedup_check: Service | None = None
    telegram_send: Service | None = None


SERVICES = NodeServices()
STRATEGIES: list[BaseStrategy] = [GVOFStrategy()]


def configure_node_services(**services: Service | None) -> None:
    valid = {field.name for field in fields(NodeServices)}
    unknown = set(services) - valid
    if unknown:
        raise ValueError(f"unknown node services: {', '.join(sorted(unknown))}")
    for name, service in services.items():
        setattr(SERVICES, name, service)


def reset_node_services() -> None:
    for field in fields(NodeServices):
        setattr(SERVICES, field.name, None)


def register_strategies(strategies: list[BaseStrategy]) -> None:
    if not all(isinstance(strategy, BaseStrategy) for strategy in strategies):
        raise TypeError("every registered strategy must inherit BaseStrategy")
    STRATEGIES[:] = strategies


async def _call(service: Service, *args: Any) -> Any:
    result = service(*args)
    return await result if inspect.isawaitable(result) else result


def _context(state: AxisState) -> dict[str, Any]:
    return state.market_context or {}


def _synthetic_block(reason: str) -> dict[str, Any]:
    return {
        "decision": "BLOCK",
        "reason": reason,
        "synthetic": True,
    }


async def calendar_gate_node(state: AxisState) -> dict:
    if SERVICES.calendar_check:
        opened = bool(await _call(SERVICES.calendar_check, state))
    else:
        opened = bool(_context(state).get("calendar_open", True))
    return {"calendar_open": opened}


async def lock_acquire_node(state: AxisState) -> dict:
    if SERVICES.lock_acquire:
        acquired = bool(await _call(SERVICES.lock_acquire, state))
    else:
        acquired = bool(_context(state).get("lock_acquired", True))
    return {"lock_acquired": acquired}


def _trust_statuses(value: Any, path: str = "market_context") -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(value, Mapping):
        if "trust_status" in value:
            found.append((path, str(value["trust_status"])))
        for key, child in value.items():
            found.extend(_trust_statuses(child, f"{path}.{key}"))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            found.extend(_trust_statuses(child, f"{path}[{index}]"))
    return found


async def data_verification_node(state: AxisState) -> dict:
    statuses = _trust_statuses(_context(state))
    degraded = any(status != "live" for _, status in statuses)
    return {
        "data_quality": {
            "sources_checked": len(statuses),
            "statuses": dict(statuses),
            "all_live": not degraded,
        },
        "degraded_mode": degraded,
    }


async def direction_scorer_node(state: AxisState) -> dict:
    context = _context(state)
    try:
        if all(key in context for key in ("layer_a", "layer_b", "layer_c", "scoring_config")):
            score = compute_direction_score(
                context["layer_a"],
                context["layer_b"],
                context["layer_c"],
                context,
            )
        else:
            score = int(context.get("direction_score", state.direction_score or 3))
        return {"direction_score": score}
    except Exception as exc:
        return {
            "direction_score": 3,
            "node_error": {"node": "direction_scorer", "message": str(exc)},
        }


async def structure_gate_node(state: AxisState) -> dict:
    context = _context(state)
    try:
        if "structure_confirmed" in context:
            confirmed = bool(context["structure_confirmed"])
        else:
            confirmed = check_structure(context.get("candles", []), context.get("chain_data", {}))
        return {"structure_confirmed": confirmed}
    except Exception as exc:
        return {
            "structure_confirmed": False,
            "node_error": {"node": "structure_gate", "message": str(exc)},
        }


async def strategy_activation_node(state: AxisState) -> dict:
    try:
        for strategy in STRATEGIES:
            result = strategy.check_conditions(state)
            if result.get("passed") is True:
                return {"active_strategy": result}
        return {"active_strategy": None}
    except Exception as exc:
        return {
            "active_strategy": None,
            "node_error": {"node": "strategy_activation", "message": str(exc)},
        }


async def analyst_node(state: AxisState) -> dict:
    try:
        if SERVICES.analyst:
            opinion = await _call(SERVICES.analyst, state)
        elif not state.active_strategy:
            opinion = None
        else:
            opinion = _context(state).get("analyst_opinion")
            if opinion is None:
                from src.llm.router import call_llm_router

                opinion = await call_llm_router("analyst", state)
        return {"analyst_opinion": opinion}
    except Exception as exc:
        return {
            "analyst_opinion": None,
            "node_error": {"node": "analyst", "message": str(exc)},
        }


async def verifier_node(state: AxisState) -> dict:
    if state.degraded_mode:
        return {"verifier_verdict": _synthetic_block("DEGRADED_DATA")}
    if not state.analyst_opinion:
        return {"verifier_verdict": _synthetic_block("ANALYST_OUTPUT_EMPTY_OR_ERRORED")}
    if state.node_error and state.node_error.get("node") == "analyst":
        return {"verifier_verdict": _synthetic_block("ANALYST_OUTPUT_EMPTY_OR_ERRORED")}
    try:
        if SERVICES.verifier:
            verdict = await _call(SERVICES.verifier, state)
        else:
            verdict = _context(state).get("verifier_verdict")
            if verdict is None:
                from src.llm.router import call_llm_router

                verdict = await call_llm_router("verifier", state)
        if not verdict:
            verdict = _synthetic_block("VERIFIER_UNAVAILABLE")
        return {"verifier_verdict": verdict}
    except Exception as exc:
        return {
            "verifier_verdict": _synthetic_block("VERIFIER_ERROR"),
            "node_error": {"node": "verifier", "message": str(exc)},
        }


def verifier_route(state: AxisState) -> str:
    verdict = state.verifier_verdict
    if isinstance(verdict, Mapping):
        decision = verdict.get("decision", verdict.get("verdict", "BLOCK"))
    else:
        decision = verdict
    return "PROCEED" if str(decision).upper() == "PROCEED" else "BLOCK"


async def risk_check_node(state: AxisState) -> dict:
    try:
        if SERVICES.risk_check:
            approved = bool(await _call(SERVICES.risk_check, state))
        else:
            approved = bool(_context(state).get("risk_approved", True))
        return {"risk_approved": approved}
    except Exception as exc:
        return {
            "risk_approved": False,
            "node_error": {"node": "risk_check", "message": str(exc)},
        }


async def dedup_node(state: AxisState) -> dict:
    now = datetime.now(IST)
    timestamp = state.cycle_timestamp
    if timestamp is not None:
        local = timestamp.replace(tzinfo=IST) if timestamp.tzinfo is None else timestamp.astimezone(IST)
        if (now - local).total_seconds() > 90:
            return {"dedup_status": "STALE_DISCARDED"}
    if not state.risk_approved:
        return {"dedup_status": "RISK_BLOCKED"}
        
    try:
        from src.journal.shadow_mode_gate import get_banknifty_shadow_status
        from src.database.supabase import get_supabase_client
        from src.database.table_routing import get_table_name
        
        symbol = state.symbol or ""
        skip_alert = False
        
        if symbol.upper() == "BANKNIFTY":
            skip_alert = True
            strategy = state.active_strategy.get("strategy_name") if state.active_strategy else None
            if strategy:
                db = get_supabase_client()
                vp_res = db.table("virtual_portfolios").select("id").eq("symbol", "BANKNIFTY").eq("strategy_name", strategy).execute()
                if vp_res.data:
                    vp_id = vp_res.data[0]["id"]
                    status = get_banknifty_shadow_status(vp_id, is_backtest=state.is_backtest)
                    if status["all_criteria_met"]:
                        skip_alert = False

        if skip_alert:
            return {"dedup_status": "SHADOW_MODE_SUPPRESSED"}

        if SERVICES.dedup_check:
            duplicate = bool(await _call(SERVICES.dedup_check, state))
        else:
            duplicate = bool(_context(state).get("duplicate_alert", False))
        return {"dedup_status": "DUPLICATE_SUPPRESSED" if duplicate else "CLEAR"}
    except Exception as exc:
        return {
            "dedup_status": "CHECK_FAILED",
            "node_error": {"node": "dedup", "message": str(exc)},
        }


async def telegram_dispatch_node(state: AxisState) -> dict:
    if state.dedup_status != "CLEAR" or not state.risk_approved:
        return {"alert_sent": False}
    try:
        if SERVICES.telegram_send:
            sent = bool(await _call(SERVICES.telegram_send, state))
        else:
            from src.delivery.alert_builder import build_alert
            from src.delivery.telegram_formatter import send_telegram_alert
            from src.config.settings import settings

            sent = send_telegram_alert(
                settings.TELEGRAM_BOT_TOKEN,
                settings.TELEGRAM_CHAT_ID,
                build_alert(state),
            )
        return {"alert_sent": sent}
    except Exception as exc:
        return {
            "alert_sent": False,
            "node_error": {"node": "telegram_dispatch", "message": str(exc)},
        }
