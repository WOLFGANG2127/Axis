"""Automated Risk Desk: Governance core for trade verification and logging."""

from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from src.database.supabase import get_supabase_client

logger = logging.getLogger("axis.risk")
IST = ZoneInfo("Asia/Kolkata")


def check_daily_drawdown() -> bool:
    """
    Evaluate both the flat frequency trigger (daily_loss_count >= 3) 
    and the dynamic magnitude trigger (current_drawdown >= max_loss_limit) 
    using strict OR logic.
    """
    from src.config.settings import settings
    mode = getattr(settings, "GOVERNANCE_DAILY_LOSS_MODE", "SHADOW")
    
    if mode == "OFF":
        return True
        
    try:
        db = get_supabase_client()
        today = datetime.now(IST).date().isoformat()
        
        # 1. Evaluate Dynamic Magnitude Trigger
        magnitude_breached = False
        res = db.table("daily_risk_limits").select("current_drawdown, max_loss_limit").eq("trading_date", today).execute()
        if res.data:
            row = res.data[0]
            current_drawdown = float(row.get("current_drawdown", 0.0))
            max_loss = float(row.get("max_loss_limit", 5000.0))
            if current_drawdown >= max_loss:
                magnitude_breached = True
                
        # 2. Evaluate Frequency Trigger (daily_loss_count >= 3)
        # Query today's losing trades from paper_trades
        today_start = datetime.now(IST).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        trades_res = db.table("paper_trades").select("pnl_rupees").gte("exit_time", today_start).execute()
        
        daily_loss_count = 0
        if trades_res.data:
            daily_loss_count = sum(1 for t in trades_res.data if t.get("pnl_rupees") is not None and float(t["pnl_rupees"]) < 0)
            
        frequency_breached = daily_loss_count >= 3
        
        # 3. Strict OR Logic
        is_breached = magnitude_breached or frequency_breached
        
        if is_breached:
            msg = (
                f"Magnitude Breached: {magnitude_breached}, Frequency Breached: {frequency_breached} "
                f"({daily_loss_count} losses)."
            )
            
            if mode == "SHADOW":
                logger.warning("SHADOW BREACH: %s (Would Block)", msg)
                try:
                    from src.delivery.telegram_formatter import send_telegram_alert
                    alert_msg = f"⚠️ [SHADOW BREACH]: Daily Loss Circuit Breaker tripped (Would Block). {msg}"
                    send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, alert_msg)
                except Exception:
                    pass
                return True
                
            elif mode == "ENFORCE":
                logger.critical("TRADE REJECTED: Daily Loss Circuit Breaker tripped. %s", msg)
                try:
                    from src.delivery.telegram_formatter import send_telegram_alert
                    alert_msg = f"🚨 ENFORCE BREACH: Daily Loss Circuit Breaker tripped. {msg}"
                    send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, alert_msg)
                except Exception:
                    pass
                return False
                
        return True
    except Exception as e:
        logger.error("Failed to verify daily drawdown: %s", e)
        return True


def validate_asymmetry(entry_price: float, stop_loss: float, take_profit: float) -> bool:
    """
    Calculate the Risk-to-Reward (R:R) ratio. 
    If it is less than 2.0, return False. Otherwise, return True.
    """
    if entry_price <= 0 or stop_loss <= 0 or take_profit <= 0:
        logger.error("Invalid prices provided to validate_asymmetry")
        return False

    risk = abs(entry_price - stop_loss)
    reward = abs(take_profit - entry_price)
    
    # Avoid division by zero if entry == stop_loss
    if risk == 0:
        logger.warning("TRADE REJECTED: Risk is zero (entry == stop loss).")
        return False
        
    reward_to_risk = reward / risk
    
    if reward_to_risk < 2.0:
        logger.warning(
            "TRADE REJECTED: R:R ratio %.2f is less than the strict 2.0 minimum.",
            reward_to_risk
        )
        return False
        
    return True


def apply_trade_tag(trade_id: int, tag_string: str) -> bool:
    """
    Insert a new row into trade_tags linking the tag_string to the specific trade.
    """
    try:
        db = get_supabase_client()
        db.table("trade_tags").insert({
            "trade_id": trade_id,
            "tag": tag_string
        }).execute()
        return True
    except Exception as e:
        logger.error("Failed to apply trade tag '%s' to trade %s: %s", tag_string, trade_id, e)
        return False
