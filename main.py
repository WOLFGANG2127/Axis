"""Local AXIS entry point: run NIFTY/BANKNIFTY signal cycles."""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from src.graph.graph import build_graph
from src.observability.correlation import new_correlation_id
from src.scheduling.calendar_gate import is_market_open, is_system_paused
from src.scheduling.lock_manager import acquire_run_lock, release_run_lock
from src.scheduling.prs_gate import check_prs_trading_gate

IST = ZoneInfo("Asia/Kolkata")
VALID_SYMBOLS = ("NIFTY", "BANKNIFTY")


def _base_market_context(now: datetime, *, lock_acquired: bool) -> dict[str, Any]:
    """Minimal safe context; live collectors enrich this before signal fire."""

    return {
        "now": now.isoformat(),
        "calendar_open": True,
        "lock_acquired": lock_acquired,
        # Conservative defaults keep the final graph runnable even when broker
        # data is unavailable. Real data/scoring fields override these.
        "direction_score": 3,
        "structure_confirmed": False,
        "risk_approved": False,
    }


def _candidate_key(candidate: dict[str, Any]) -> str:
    return str(candidate.get("strategy_id") or candidate.get("strategy_name") or "gvof").strip().lower().replace(" ", "_")


def _verdict_decision(verdict: Any) -> str:
    if isinstance(verdict, dict):
        return str(verdict.get("decision", verdict.get("verdict", "BLOCK"))).upper()
    return str(verdict or "BLOCK").upper()


def _proceed_candidates(result: dict[str, Any]) -> list[dict[str, Any]]:
    verdicts = result.get("verifier_verdicts") or {}
    return [
        candidate
        for candidate in (result.get("candidate_signals") or [])
        if _verdict_decision(verdicts.get(_candidate_key(candidate))) == "PROCEED"
    ]


def _verifier_decision(result: dict[str, Any]) -> str:
    return "PROCEED" if _proceed_candidates(result) else "BLOCK"


def _candidate_direction(candidate: dict[str, Any]) -> str:
    return str(candidate.get("direction", "")).strip().lower()


def _strategy_direction(result: dict[str, Any]) -> str:
    candidates = _proceed_candidates(result)
    if not candidates:
        return ""
    return _candidate_direction(candidates[0])


def _proceed_directions(result: dict[str, Any]) -> set[str]:
    return {direction for candidate in _proceed_candidates(result) if (direction := _candidate_direction(candidate))}


def _haircut_candidate(candidate: dict[str, Any], *, other_symbol: str, other_direction: str) -> dict[str, Any]:
    strategy = dict(candidate)
    lots = int(strategy.get("lots") or 0)
    if lots > 0:
        new_lots = max(1, lots // 2)
        ratio = new_lots / lots
        strategy["lots"] = new_lots
        if "capital_deployed" in strategy:
            strategy["capital_deployed"] = float(strategy["capital_deployed"]) * ratio
        if "risk_rupees" in strategy:
            strategy["risk_rupees"] = float(strategy["risk_rupees"]) * ratio
    strategy["alert_tag"] = f"CORRELATED SIGNAL - {other_symbol} {other_direction.upper()} same-cycle"
    strategy["cross_symbol_haircut_applied"] = True
    return strategy


def _haircut_correlated_strategy(result: dict[str, Any], *, other_symbol: str, correlated_directions: set[str]) -> None:
    proceed_keys = {_candidate_key(candidate) for candidate in _proceed_candidates(result)}
    updated = []
    for candidate in result.get("candidate_signals") or []:
        direction = _candidate_direction(candidate)
        if _candidate_key(candidate) in proceed_keys and direction in correlated_directions:
            updated.append(_haircut_candidate(candidate, other_symbol=other_symbol, other_direction=direction))
        else:
            updated.append(candidate)
    result["candidate_signals"] = updated


def apply_same_cycle_correlation(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Apply the cross-symbol haircut to same-cycle same-direction signals."""

    by_symbol = {
        str(result.get("symbol", "")).upper(): result
        for result in results
        if str(result.get("symbol", "")).upper() in VALID_SYMBOLS
    }
    if set(by_symbol) != set(VALID_SYMBOLS):
        return results
    nifty = by_symbol["NIFTY"]
    bank = by_symbol["BANKNIFTY"]
    if _verifier_decision(nifty) != "PROCEED" or _verifier_decision(bank) != "PROCEED":
        return results
    correlated_directions = _proceed_directions(nifty) & _proceed_directions(bank)
    if not correlated_directions:
        return results
    _haircut_correlated_strategy(nifty, other_symbol="BANKNIFTY", correlated_directions=correlated_directions)
    _haircut_correlated_strategy(bank, other_symbol="NIFTY", correlated_directions=correlated_directions)
    return results


def _commit_macro_regime_flags(results: list[dict[str, Any]], *, db: Any | None = None) -> None:
    database = db
    if database is None:
        try:
            from src.database.supabase import get_supabase_client

            database = get_supabase_client()
        except Exception:
            return
    now = datetime.now(IST).isoformat()
    for result in results:
        if _verifier_decision(result) != "PROCEED":
            continue
        symbol = str(result.get("symbol", "")).upper()
        if symbol not in VALID_SYMBOLS:
            continue
        for candidate in _proceed_candidates(result):
            direction = _candidate_direction(candidate)
            if not direction:
                continue
            try:
                database.table("macro_regime_flags").insert(
                    {
                        "symbol": symbol,
                        "direction": direction,
                        "signal_timestamp": now,
                        "session_id": result.get("correlation_id") or "SYS",
                    }
                ).execute()
            except Exception:
                continue


def _dispatch_deferred_alerts(results: list[dict[str, Any]]) -> None:
    try:
        from src.config.settings import settings
        from src.delivery.alert_builder import build_alert
        from src.delivery.telegram_formatter import send_telegram_alert
        from src.graph.state import AxisState
    except Exception:
        return

    fields = set(AxisState.model_fields)
    for result in results:
        if result.get("risk_approved") is not True or result.get("dedup_status") != "CLEAR":
            continue
        for candidate in _proceed_candidates(result):
            try:
                state_payload = {key: value for key, value in result.items() if key in fields}
                state_payload["candidate_signals"] = [candidate]
                state_payload["verifier_verdicts"] = {
                    _candidate_key(candidate): (result.get("verifier_verdicts") or {}).get(_candidate_key(candidate), {})
                }
                state = AxisState(**state_payload)
                result["alert_sent"] = send_telegram_alert(
                    settings.TELEGRAM_BOT_TOKEN,
                    settings.TELEGRAM_CHAT_ID,
                    build_alert(state),
                )
            except Exception:
                result["alert_sent"] = False


async def run_cycle(
    symbol: str,
    *,
    db: Any | None = None,
    now: datetime | None = None,
    graph: Any | None = None,
) -> dict[str, Any]:
    """Run exactly one local AXIS cycle and always release the run lock."""

    normalized = symbol.strip().upper()
    if normalized not in VALID_SYMBOLS:
        raise ValueError("symbol must be NIFTY or BANKNIFTY")

    current = (now or datetime.now(IST)).astimezone(IST)

    # The calendar gate is intentionally the first operational check.
    if not is_market_open(current):
        return {"status": "MARKET_CLOSED", "symbol": normalized}

    paused, reason = is_system_paused(db=db)
    if paused:
        return {"status": "SYSTEM_PAUSED", "symbol": normalized, "reason": reason}

    prs_gate = check_prs_trading_gate(db=db, now=current)
    if not prs_gate.allowed:
        return {
            "status": "PRS_BLOCKED",
            "symbol": normalized,
            "reason": prs_gate.reason,
            "cutoff_ist": prs_gate.cutoff_ist,
        }

    acquired = acquire_run_lock(normalized, db=db, now=current)
    if not acquired:
        return {"status": "LOCK_HELD", "symbol": normalized}

    correlation_id = new_correlation_id()
    try:
        runnable = graph or build_graph()
        state = {
            "symbol": normalized,
            "cycle_timestamp": current,
            "correlation_id": correlation_id,
            "market_context": _base_market_context(current, lock_acquired=True),
        }
        result = await runnable.ainvoke(state)
        result["status"] = "COMPLETED"
        result["correlation_id"] = result.get("correlation_id") or correlation_id
        return result
    finally:
        release_run_lock(normalized, db=db)


async def run_all_symbols_cycle(
    *,
    db: Any | None = None,
    now: datetime | None = None,
    graph: Any | None = None,
) -> dict[str, Any]:
    """Run NIFTY then BANKNIFTY in one process to close the matrix race."""

    current = (now or datetime.now(IST)).astimezone(IST)
    if not is_market_open(current):
        return {"status": "MARKET_CLOSED", "results": []}
    paused, reason = is_system_paused(db=db)
    if paused:
        return {"status": "SYSTEM_PAUSED", "reason": reason, "results": []}

    prs_gate = check_prs_trading_gate(db=db, now=current)
    if not prs_gate.allowed:
        return {
            "status": "PRS_BLOCKED",
            "reason": prs_gate.reason,
            "cutoff_ist": prs_gate.cutoff_ist,
            "results": [],
        }

    runnable = graph or build_graph()
    acquired: list[str] = []
    results: list[dict[str, Any]] = []
    try:
        for symbol in VALID_SYMBOLS:
            if not acquire_run_lock(symbol, db=db, now=current):
                results.append({"symbol": symbol, "status": "LOCK_HELD"})
                continue
            acquired.append(symbol)
            try:
                correlation_id = new_correlation_id()
                context = _base_market_context(current, lock_acquired=True)
                context["defer_cross_symbol_coordination"] = True
                context["defer_telegram_dispatch"] = True
                state = {
                    "symbol": symbol,
                    "cycle_timestamp": current,
                    "correlation_id": correlation_id,
                    "market_context": context,
                }
                result = await runnable.ainvoke(state)
                result["status"] = "COMPLETED"
                result["symbol"] = result.get("symbol") or symbol
                result["correlation_id"] = result.get("correlation_id") or correlation_id
                results.append(result)
            except Exception as exc:
                results.append({"symbol": symbol, "status": "ERROR", "error": str(exc)})
        apply_same_cycle_correlation(results)
        _commit_macro_regime_flags(results, db=db)
        _dispatch_deferred_alerts(results)
        return {"status": "COMPLETED", "results": results}
    finally:
        for symbol in acquired:
            release_run_lock(symbol, db=db)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run AXIS signal cycle(s).")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--symbol", choices=VALID_SYMBOLS)
    group.add_argument("--all", action="store_true", help="Run NIFTY then BANKNIFTY sequentially")
    return parser


async def _amain() -> None:
    args = _parser().parse_args()
    result = await run_all_symbols_cycle() if args.all else await run_cycle(args.symbol)
    print(result)


if __name__ == "__main__":
    asyncio.run(_amain())

def _send_pipeline_crash_alert(exc: BaseException) -> None:
    try:
        from src.config.settings import settings
        from src.delivery.telegram_formatter import send_telegram_alert
        send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, f"AXIS PIPELINE CRASHED\n\n{type(exc).__name__}: {exc}")
    except Exception:
        pass


def _run_cli() -> None:
    try:
        asyncio.run(_amain())
    except Exception as exc:
        _send_pipeline_crash_alert(exc)
        raise
