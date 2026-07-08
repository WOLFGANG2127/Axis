"""Local AXIS entry point: run one NIFTY/BANKNIFTY signal cycle."""

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


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one AXIS signal cycle.")
    parser.add_argument("--symbol", required=True, choices=VALID_SYMBOLS)
    return parser


async def _amain() -> None:
    args = _parser().parse_args()
    result = await run_cycle(args.symbol)
    print(result)


if __name__ == "__main__":
    asyncio.run(_amain())
