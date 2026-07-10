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
        .select("*")
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
    
    # 2.4 Behavioral Auto-Tagging
    auto_tag = None
    checklist = trade.get("pre_trade_checklist") or {}
    if isinstance(checklist, str):
        import json
        try:
            checklist = json.loads(checklist)
        except Exception:
            checklist = {}
            
    # 1. Check OVERSIZE_CONVICTION
    actual_lots = trade.get("lots") or trade.get("quantity") or checklist.get("lots") or 0
    kelly_lots = checklist.get("kelly_recommended_lots") or checklist.get("recommended_lots")
    
    if actual_lots and kelly_lots:
        # Boundary: > 1.25 is oversized. Exactly 1.25x is considered safe.
        if float(actual_lots) > (float(kelly_lots) * 1.25):
            auto_tag = "OVERSIZE_CONVICTION"

    # 2. Check REVENGE_TRADE
    entry_time_str = trade.get("entry_time")
    if entry_time_str:
        # Find the exit time of the last recorded losing trade BEFORE this entry
        last_loss_res = (
            database.table(get_table_name("paper_trades", is_backtest))
            .select("exit_time")
            .lt("pnl_rupees", 0)
            .lt("exit_time", entry_time_str)
            .order("exit_time", desc=True)
            .limit(1)
            .execute()
        )
        if last_loss_res.data and last_loss_res.data[0].get("exit_time"):
            last_loss_exit = datetime.fromisoformat(str(last_loss_res.data[0]["exit_time"]).replace("Z", "+00:00")).astimezone(IST)
            entry_time = datetime.fromisoformat(str(entry_time_str).replace("Z", "+00:00")).astimezone(IST)
            
            diff_minutes = (entry_time - last_loss_exit).total_seconds() / 60.0
            
            # Boundary: < 20.0 minutes is revenge. Exactly 20.0 minutes is considered safe.
            if diff_minutes < 20.0:
                auto_tag = "REVENGE_TRADE" # This correctly overwrites OVERSIZE_CONVICTION if both occur
                
    if auto_tag:
        row["behavioral_outcome_category"] = auto_tag
        row["behavioral_tag_auto"] = True
        row["behavioral_tag_source"] = "AUTO"
    else:
        row["behavioral_outcome_category"] = "PENDING"
        row["behavioral_tag_auto"] = False
        row["behavioral_tag_source"] = "PENDING"
        
    # 2.6 Signal Metadata Population (Outcome Time)
    signal_metadata = checklist.get("signal_metadata", {})
    
    # Set fields computable at outcome time
    signal_metadata["actual_fill_price"] = trade.get("entry_price", trade.get("exit_price"))
    
    # Using the local diff_minutes calculated for the REVENGE_TRADE check
    if 'diff_minutes' in locals():
        signal_metadata["entry_minutes_since_last_loss"] = diff_minutes
    else:
        signal_metadata["entry_minutes_since_last_loss"] = None
        
    # These explicitly require follow-up jobs/backfills
    signal_metadata["simulated_pyramided_pnl"] = None
    signal_metadata["realized_direction_next_60min"] = None
    
    row["signal_metadata"] = signal_metadata
        
    response = database.table("trade_outcomes").insert(row).execute()
    
    # Outbound Behavioral Prompt (Prompt 27)
    if not auto_tag:
        try:
            from src.delivery.telegram_formatter import send_behavioral_rating_prompt
            from src.config.settings import settings
            send_behavioral_rating_prompt(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, paper_trade_id)
        except Exception as e:
            import logging
            logging.getLogger("axis.journal").error("Failed to send behavioral prompt: %s", e)
    
    # 2.3 Compute and Update Dynamic Drawdown Limit
    _update_dynamic_drawdown_limit(database, is_backtest)
    
    return (response.data or [row])[0]

def _update_dynamic_drawdown_limit(db: Any, is_backtest: bool) -> None:
    import numpy as np
    
    try:
        table_name = get_table_name("paper_trades", is_backtest)
        thirty_days_ago = (datetime.now(IST) - timedelta(days=30)).isoformat()
        
        # Query past 30 calendar days of realized daily net P&L
        res = db.table(table_name).select("exit_time, pnl_rupees").gte("exit_time", thirty_days_ago).execute()
        trades = res.data or []
        
        daily_pnl = {}
        for t in trades:
            if not t.get("exit_time") or t.get("pnl_rupees") is None:
                continue
            dt = datetime.fromisoformat(str(t["exit_time"]).replace("Z", "+00:00")).astimezone(IST)
            date_str = dt.date().isoformat()
            daily_pnl[date_str] = daily_pnl.get(date_str, 0.0) + float(t["pnl_rupees"])
                
        pnl_array = np.array(list(daily_pnl.values()))
        
        if len(pnl_array) < 3:
            dynamic_limit = 5000.0
        else:
            sigma = np.std(pnl_array)
            three_sigma = abs(3.0 * sigma)
            
            losing_days = pnl_array[pnl_array < 0]
            if len(losing_days) < 5:
                # Handle fallback if fewer than 5 losing days
                dynamic_limit = 5000.0
            else:
                p95_loss = float(np.percentile(np.abs(losing_days), 95))
                # Select the smaller of the two absolute values
                dynamic_limit = min(three_sigma, p95_loss)
                
            dynamic_limit = max(dynamic_limit, 1000.0) # Safe minimum clamp
            
        today = datetime.now(IST).date().isoformat()
        # Update max_loss_limit for today
        existing = db.table("daily_risk_limits").select("current_drawdown").eq("trading_date", today).execute()
        if existing.data:
            db.table("daily_risk_limits").update({"max_loss_limit": float(dynamic_limit)}).eq("trading_date", today).execute()
        else:
            db.table("daily_risk_limits").insert({"trading_date": today, "max_loss_limit": float(dynamic_limit)}).execute()
            
    except Exception as e:
        import logging
        logging.getLogger("axis.journal").error("Failed to update dynamic drawdown limit: %s", e)

def process_behavioral_rating(score: str, trade_id: Any = None) -> bool:
    """
    Process an inbound behavioral rating from the user via the webhook.
    If trade_id is provided, verify it. Otherwise, fallback to the most recent PENDING trade.
    Returns True if processed, False if ignored (e.g., if clicked hours late and no PENDING exists).
    """
    db = get_supabase_client()
    
    if trade_id:
        res = db.table("trade_outcomes").select("id, behavioral_tag_source").eq("paper_trade_id", trade_id).execute()
        if not res.data or res.data[0].get("behavioral_tag_source") != "PENDING":
            return False
        target_id = res.data[0]["id"]
    else:
        # Fallback: Find the most recent PENDING trade
        res = db.table("trade_outcomes").select("id").eq("behavioral_tag_source", "PENDING").order("id", desc=True).limit(1).execute()
        if not res.data:
            return False
        target_id = res.data[0]["id"]
        
    score_map = {
        "5": "USER_PERFECT",
        "4": "USER_GOOD",
        "3": "USER_AVERAGE",
        "2": "USER_POOR",
        "1": "USER_TILT"
    }
    
    clean_score = str(score).strip()
    category = score_map.get(clean_score, f"USER_SCORE_{clean_score}")
    
    try:
        db.table("trade_outcomes").update({
            "behavioral_outcome_category": category,
            "behavioral_tag_source": "USER"
        }).eq("id", target_id).execute()
        return True
    except Exception as e:
        import logging
        logging.getLogger("axis.journal").error("Failed to update behavioral rating: %s", e)
        return False
