"""No-Trade Day cron: Calculates and reports friction/losses avoided when no trades are taken."""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from src.database.supabase import get_supabase_client
from src.delivery.telegram_formatter import send_telegram_alert
from src.config.settings import settings

logger = logging.getLogger("axis.scheduling")
IST = ZoneInfo("Asia/Kolkata")

def run_no_trade_summary() -> None:
    try:
        db = get_supabase_client()
        now = datetime.now(IST)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        
        # 1. Check if any trades were executed today
        res = db.table("paper_trades").select("id").gte("exit_time", today_start).execute()
        today_trades = res.data or []
        
        if len(today_trades) > 0:
            logger.info("Trades were taken today. Skipping No-Trade Day summary.")
            return
            
        # 2. Calculate average daily loss
        # Fetch all trades to compute average loss per losing trade/day
        hist_res = db.table("paper_trades").select("pnl_rupees").lt("pnl_rupees", 0).execute()
        losing_trades = hist_res.data or []
        
        avg_loss = 0.0
        if losing_trades:
            total_loss = sum(abs(float(t["pnl_rupees"])) for t in losing_trades if t.get("pnl_rupees") is not None)
            avg_loss = total_loss / len(losing_trades)
        else:
            avg_loss = 2500.0 # Fallback empirical estimate
            
        # Estimated friction per trade (brokerage, STT, exchange, GST)
        # Using a fixed conservative estimate for unexecuted volume
        estimated_friction = 150.0 * 2 
            
        # 3. Format and send summary
        msg = (
            "🧘‍♂️ **No-Trade Day Summary**\n\n"
            "Discipline maintained. Zero trades executed today.\n\n"
            "🛡️ **Capital Preserved:**\n"
            f"• Estimated Friction Avoided: ₹{estimated_friction:.2f}\n"
            f"• Average Historical Loss Avoided: ₹{avg_loss:.2f}\n\n"
            "Sitting on hands is a valid position. Rest up for tomorrow."
        )
        
        send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, msg)
        logger.info("Successfully dispatched No-Trade Day summary.")
        
    except Exception as e:
        logger.error("Failed to execute No-Trade Day summary: %s", e)

if __name__ == "__main__":
    run_no_trade_summary()
