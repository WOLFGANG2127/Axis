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
    context = _context(state)
    if state.symbol and context.get("candles"):
        try:
            from src.data.ohlc_writer import persist_ohlc_candles

            persist_ohlc_candles(
                symbol=state.symbol,
                candles=context.get("candles"),
                interval=str(context.get("candle_interval") or "5"),
                cycle_timestamp=state.cycle_timestamp,
                correlation_id=state.correlation_id,
            )
        except Exception as exc:
            _log.error("OHLC persistence failed for %s: %s", state.symbol, exc)
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
        
    from src.risk.risk_manager import check_daily_drawdown, validate_asymmetry, apply_trade_tag
    
    # 1. Drawdown Check
    if not check_daily_drawdown():
        try:
            from src.delivery.telegram_formatter import send_telegram_alert
            from src.config.settings import settings
            msg = "Trade blocked: Daily max loss limit reached"
            send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, msg)
        except Exception:
            pass
        return {"verifier_verdict": _synthetic_block("MAX_LOSS_LIMIT_REACHED")}
        
    # 2. Asymmetry Check
    strategy = state.active_strategy or {}
    entry = float(strategy.get("entry", 0.0))
    sl = float(strategy.get("stop_loss", 0.0))
    # We use target_1 as the primary payoff threshold
    tp = float(strategy.get("target_1", 0.0))
    
    if entry > 0 and sl > 0 and tp > 0:
        if not validate_asymmetry(entry, sl, tp):
            # 3. Tagging / Logging
            # Since the trade is blocked pre-execution, we use a synthetic block tag
            # instead of a DB trade_id tag.
            return {"verifier_verdict": _synthetic_block("SUBOPTIMAL_RR")}
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
            
        if isinstance(verdict, Mapping):
            decision = verdict.get("decision", verdict.get("verdict", "BLOCK"))
        else:
            decision = str(verdict)
            
        ret: dict[str, Any] = {"verifier_verdict": verdict}
        
        if str(decision).upper() == "PROCEED":
            try:
                from src.database.supabase import get_supabase_client
                import math
                from datetime import timedelta
                
                db = get_supabase_client()
                now = datetime.now(IST)
                sixty_mins_ago = (now - timedelta(minutes=60)).isoformat()
                
                my_symbol = (state.symbol or "").upper()
                my_dir = strategy.get("direction", "").lower()
                other_symbol = "BANKNIFTY" if my_symbol == "NIFTY" else "NIFTY"
                
                # 1. Query macro_regime_flags for the other symbol
                flags_res = db.table("macro_regime_flags") \
                    .select("*") \
                    .eq("symbol", other_symbol) \
                    .gte("signal_timestamp", sixty_mins_ago) \
                    .order("signal_timestamp", desc=True) \
                    .limit(1) \
                    .execute()
                    
                if flags_res.data and my_dir:
                    other_flag = flags_res.data[0]
                    other_dir = other_flag.get("direction", "").lower()
                    other_time = other_flag.get("signal_timestamp")
                    
                    # 2. Hedging vs. Correlation Gate
                    if other_dir == my_dir:
                        # Same-direction correlation: Apply risk reduction
                        orig_lots = strategy.get("lots", 0)
                        if orig_lots > 0:
                            new_lots = max(1, math.floor(orig_lots / 2))
                            # Proportionally reduce capital/risk
                            reduction_ratio = new_lots / orig_lots
                            
                            strategy["lots"] = new_lots
                            if "capital_deployed" in strategy:
                                strategy["capital_deployed"] *= reduction_ratio
                            if "risk_rupees" in strategy:
                                strategy["risk_rupees"] *= reduction_ratio
                                
                            # 4. Inject Tag
                            tag_time = datetime.fromisoformat(str(other_time).replace("Z", "+00:00")).astimezone(IST).strftime("%H:%M")
                            strategy["alert_tag"] = f"⚠️ CORRELATED SIGNAL — {other_symbol} {other_dir.capitalize()} at {tag_time}"
                            ret["active_strategy"] = strategy
                            
                # 5. Insert current signal's data into macro_regime_flags
                if my_symbol and my_dir:
                    db.table("macro_regime_flags").insert({
                        "symbol": my_symbol,
                        "direction": my_dir,
                        "signal_timestamp": now.isoformat(),
                        "session_id": "SYS" # Fallback since session_id isn't directly in AxisState
                    }).execute()
                    
                # 6. Capture Signal Metadata
                trades_res = db.table("paper_trades").select("exit_time,pnl_rupees").order("exit_time", desc=True).limit(10).execute()
                recent_trades = trades_res.data or []
                win_streak = 0
                loss_streak = 0
                for t in recent_trades:
                    pnl = float(t.get("pnl_rupees") or 0)
                    if pnl > 0:
                        if loss_streak > 0: break
                        win_streak += 1
                    elif pnl < 0:
                        if win_streak > 0: break
                        loss_streak += 1
                        
                hours_since_last = None
                if recent_trades and recent_trades[0].get("exit_time"):
                    last_exit = datetime.fromisoformat(str(recent_trades[0]["exit_time"]).replace("Z", "+00:00")).astimezone(IST)
                    hours_since_last = (now - last_exit).total_seconds() / 3600.0
                    
                kelly_lots = _context(state).get("kelly_recommended_lots") or strategy.get("kelly_recommended_lots")
                actual_lots = strategy.get("lots", 0)
                kelly_ratio = (actual_lots / float(kelly_lots)) if (kelly_lots and float(kelly_lots) > 0) else None
                
                strategy["signal_metadata"] = {
                    "stage1_entry_price": strategy.get("entry"),
                    "stage1_lots": actual_lots,
                    "level_held_bool": _context(state).get("closed_back_in_zone"),
                    "stage2_hypothetical_trigger_price": None, # Post-trade compute
                    "stage2_would_have_fired_bool": None, # Post-trade compute
                    "alert_price": strategy.get("entry"),
                    "fii_long_short_ratio_at_signal": _context(state).get("fii_long_short_ratio"),
                    "hours_since_last_trade_session_end": hours_since_last,
                    "time_of_day_entered": now.isoformat(),
                    "win_streak_count_at_entry": win_streak,
                    "loss_streak_count_at_entry": loss_streak,
                    "lots_taken_vs_kelly_recommended_ratio": kelly_ratio,
                    # Outcome time fields (NULL at signal time)
                    "actual_fill_price": None,
                    "simulated_pyramided_pnl": None,
                    "realized_direction_next_60min": None,
                    "entry_minutes_since_last_loss": None
                }
                ret["active_strategy"] = strategy
                
            except Exception as e:
                import logging
                logging.getLogger("axis.risk").error("Cross-symbol coordination failed: %s", e)
                
        return ret
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
