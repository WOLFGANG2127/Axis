"""Weekly Friction Tracker: Calculates annualized run-rate of trading costs."""

import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.database.supabase import get_supabase_client
from src.delivery.telegram_formatter import send_telegram_alert
from src.config.settings import settings

logger = logging.getLogger("axis.delivery")
IST = ZoneInfo("Asia/Kolkata")

def run_weekly_friction_report() -> None:
    try:
        db = get_supabase_client()
        now = datetime.now(IST)
        # Past 7 days
        week_ago = (now - timedelta(days=7)).replace(hour=0, minute=0, second=0).isoformat()
        
        res = db.table("paper_trades").select("id,lots").gte("exit_time", week_ago).execute()
        trades = res.data or []
        
        total_trades = len(trades)
        
        # Estimate friction: Brokerage + STT + SEBI + Stamp + GST
        # Typical round-trip for an index options trade in India is ~80 to 120 INR per trade depending on lots.
        # Conservatively estimating 150 INR per trade for the run-rate projection.
        weekly_friction = total_trades * 150.0
        
        annualized_friction = weekly_friction * 52.0
        
        msg = (
            "📉 **Weekly Friction Report**\n\n"
            f"Total Trades This Week: {total_trades}\n"
            f"Estimated Weekly Transaction Costs: ₹{weekly_friction:,.2f}\n"
            f"**Annualized Run-Rate Drag:** ₹{annualized_friction:,.2f}\n\n"
            "_Costs include Brokerage, STT, Exchange Fees, SEBI, Stamp Duty, and GST._"
        )
        
        send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, msg)
        logger.info("Successfully dispatched Weekly Friction Report.")
        
    except Exception as e:
        logger.error("Failed to execute Weekly Friction Report: %s", e)

if __name__ == "__main__":
    run_weekly_friction_report()
