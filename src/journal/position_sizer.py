"""The single authoritative position-sizing implementation."""

from __future__ import annotations

import math
from datetime import datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from src.config.constants import KELLY_CAP_PCT, KELLY_MIN_SAMPLE, RISK_FLAT_PCT
from src.database.supabase import get_supabase_client
from src.database.table_routing import get_table_name
from src.journal.accuracy_engine import get_position_sizing_stats
from src.math.pricing import kelly_fraction

IST = ZoneInfo("Asia/Kolkata")


class InsufficientCapitalError(RuntimeError):
    """Raised when capital, risk budget, or the weekly stop forbids entry."""


def _database(db: Any | None) -> Any:
    return db if db is not None else get_supabase_client()


def _portfolio(strategy: str, symbol: str, db: Any, is_backtest: bool = False) -> dict[str, Any]:
    rows = (
        db.table("virtual_portfolios")
        .select("id,current_capital,initial_capital,weekly_loss_limit_pct")
        .eq("strategy_name", strategy)
        .eq("symbol", symbol)
        .limit(2)
        .execute()
        .data
        or []
    )
    if len(rows) != 1:
        raise InsufficientCapitalError(
            f"expected one virtual portfolio for ({strategy}, {symbol}); found {len(rows)}"
        )
    return rows[0]


def _weekly_loss(portfolio_id: Any, db: Any, now: datetime, is_backtest: bool = False) -> float:
    local = now.replace(tzinfo=IST) if now.tzinfo is None else now.astimezone(IST)
    week_start = datetime.combine(
        local.date() - timedelta(days=local.weekday()), time.min, tzinfo=IST
    )
    rows = (
        db.table(get_table_name("paper_trades", is_backtest))
        .select("pnl_rupees")
        .eq("virtual_portfolio_id", portfolio_id)
        .gte("exit_time", week_start.isoformat())
        .lt("exit_time", (week_start + timedelta(days=7)).isoformat())
        .execute()
        .data
        or []
    )
    return sum(abs(float(row["pnl_rupees"])) for row in rows if float(row.get("pnl_rupees") or 0) < 0)


def calculate_position(
    strategy: str,
    symbol: str,
    entry: float,
    stop: float,
    lot_size: int,
    *,
    db: Any | None = None,
    now: datetime | None = None,
    is_backtest: bool = False,
) -> dict[str, int | float]:
    """Apply weekly stop, cold-start 1%, then half-Kelly capped at 2%."""
    if entry <= 0 or stop <= 0 or entry == stop or lot_size <= 0:
        raise ValueError("entry, stop, and lot_size must define positive non-zero risk")
    database = _database(db)
    portfolio = _portfolio(strategy, symbol, database, is_backtest)
    current_capital = float(portfolio["current_capital"])
    initial_capital = float(portfolio["initial_capital"])
    limit_pct = float(portfolio["weekly_loss_limit_pct"])
    if limit_pct > 1:
        limit_pct /= 100.0
    loss = _weekly_loss(portfolio["id"], database, now or datetime.now(IST), is_backtest)
    if loss >= initial_capital * limit_pct:
        raise InsufficientCapitalError(
            f"weekly loss limit reached for {strategy}/{symbol}: {loss:.2f}"
        )

    stats = get_position_sizing_stats(strategy, symbol, db=database, is_backtest=is_backtest)
    risk_pct = RISK_FLAT_PCT
    if stats and int(stats["sample_count"]) >= KELLY_MIN_SAMPLE:
        full_kelly = kelly_fraction(
            float(stats["win_rate"]),
            float(stats["avg_gain"]),
            float(stats["avg_loss"]),
        )
        risk_pct = min(KELLY_CAP_PCT, max(0.0, full_kelly / 2.0))
    risk_per_lot = abs(entry - stop) * lot_size
    risk_budget = current_capital * risk_pct
    lots = math.floor(risk_budget / risk_per_lot) if risk_per_lot else 0
    if lots < 1:
        raise InsufficientCapitalError(
            f"risk budget {risk_budget:.2f} cannot fund one lot risking {risk_per_lot:.2f}"
        )
        
    # TODO (Tier 5): NIFTY's effective freeze quantity is 1,755 units (27 lots) at lot size 65. BankNifty's equivalent freeze quantity needs confirming before Tier 5 pyramid execution work begins.
    
    return {
        "lots": lots,
        "capital_deployed": float(lots * lot_size * entry),
        "risk_rupees": float(lots * risk_per_lot),
    }

