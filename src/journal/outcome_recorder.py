"""Post-exit outcome sampling and constrained loss taxonomy."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Mapping
from zoneinfo import ZoneInfo

from src.database.supabase import get_supabase_client
from src.database.table_routing import get_table_name
from src.scoring.layer_a import classify_vix_move

IST = ZoneInfo("Asia/Kolkata")
HORIZONS = (15, 30, 60, 120)
LOSS_CATEGORIES = {
    "STRUCTURE_SIGNAL_IGNORED",
    "ZONE_INTEGRITY_MISREAD",
    "TIME_DECAY_MISJUDGED",
    "OI_WALL_UNDERWEIGHTED",
}


def _database(db: Any | None) -> Any:
    return db if db is not None else get_supabase_client()


def _one(rows: list[dict[str, Any]], description: str) -> dict[str, Any]:
    if len(rows) != 1:
        raise LookupError(f"expected one {description}; found {len(rows)}")
    return rows[0]


def _loss_category(trade: Mapping[str, Any]) -> str | None:
    if float(trade.get("pnl_rupees") or 0) >= 0:
        return None
    checklist = trade.get("pre_trade_checklist") or {}
    if isinstance(checklist, str):
        import json

        checklist = json.loads(checklist)
    if checklist.get("structure_signal_ignored"):
        return "STRUCTURE_SIGNAL_IGNORED"
    if checklist.get("zone_integrity_misread") or checklist.get("at_vp_boundary") is False:
        return "ZONE_INTEGRITY_MISREAD"
    if checklist.get("time_decay_misjudged") or checklist.get("theta_viable") is False:
        return "TIME_DECAY_MISJUDGED"
    if checklist.get("oi_wall_underweighted"):
        return "OI_WALL_UNDERWEIGHTED"
    return None


def record_outcome(paper_trade_id: Any, *, db: Any | None = None, is_backtest: bool = False) -> dict[str, Any]:
    """Sample cached index candles and insert exactly one outcome row."""
    database = _database(db)
    trade = _one(
        database.table(get_table_name("paper_trades", is_backtest))
        .select("id,symbol,exit_time,exit_price,pnl_rupees,pre_trade_checklist")
        .eq("id", paper_trade_id)
        .limit(2)
        .execute()
        .data
        or [],
        "paper trade",
    )
    if not trade.get("exit_time"):
        raise ValueError("paper trade has no exit_time")
    exit_time = datetime.fromisoformat(str(trade["exit_time"]).replace("Z", "+00:00")).astimezone(IST)
    sampled: dict[int, float | None] = {}
    last_row: dict[str, Any] | None = None
    for minutes in HORIZONS:
        target = exit_time + timedelta(minutes=minutes)
        rows = (
            database.table("cached_candles")
            .select("timestamp,close,vix_change_pct,spot_move_pct")
            .eq("symbol", trade["symbol"])
            .gte("timestamp", target.isoformat())
            .order("timestamp")
            .limit(1)
            .execute()
            .data
            or []
        )
        last_row = rows[0] if rows else last_row
        sampled[minutes] = float(rows[0]["close"]) if rows else None
    vix_class = (
        classify_vix_move(
            float(last_row.get("vix_change_pct") or 0),
            float(last_row.get("spot_move_pct") or 0),
        )
        if last_row
        else "normal"
    )
    category = _loss_category(trade)
    if category is not None and category not in LOSS_CATEGORIES:
        raise ValueError(f"invalid outcome category: {category}")
    row = {
        "paper_trade_id": paper_trade_id,
        "price_15m": sampled[15],
        "price_30m": sampled[30],
        "price_60m": sampled[60],
        "price_120m": sampled[120],
        "post_exit_vix_classification": vix_class,
        "outcome_category": category,
    }
    response = database.table("trade_outcomes").insert(row).execute()
    return (response.data or [row])[0]

