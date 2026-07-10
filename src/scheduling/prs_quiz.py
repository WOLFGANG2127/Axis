"""Personal Readiness Score (PRS) Module."""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
import requests

from src.database.supabase import get_supabase_client
from src.config.settings import settings

logger = logging.getLogger("axis.prs")
IST = ZoneInfo("Asia/Kolkata")

def send_prs_quiz() -> None:
    """Send the Morning Readiness Quiz via Telegram inline keyboard."""
    
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # Q1 of the PRS Quiz
    text = (
        "🌅 **Morning Personal Readiness Score (PRS)**\n\n"
        "Let's assess your readiness to trade today.\n"
        "**Q1/3: How was your Sleep Quality?**"
    )
    
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "Excellent (3)", "callback_data": "prs_sleep_3"},
                {"text": "Average (2)", "callback_data": "prs_sleep_2"},
                {"text": "Poor (1)", "callback_data": "prs_sleep_1"}
            ]
        ]
    }
    
    try:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "reply_markup": reply_markup,
            },
            timeout=10.0,
        )
        response.raise_for_status()
        logger.info("Successfully dispatched PRS Quiz (Q1).")
        
        # Initialize state for today
        db = get_supabase_client()
        today = datetime.now(IST).date().isoformat()
        
        # Ensure a session state row exists for today
        existing = db.table("trader_session_state").select("id").eq("trading_date", today).execute()
        if not existing.data:
            db.table("trader_session_state").insert({
                "trading_date": today,
                "is_trading_blocked": False, # Open until proven otherwise
                "prs_score": 0,
                "prs_completed": False
            }).execute()
            
    except Exception as e:
        logger.error("Failed to send PRS Quiz: %s", e)

def process_prs_callback(callback_data: str, message_id: int) -> None:
    """
    Called by the webhook to process PRS answers, advance the quiz, 
    and calculate the final composite score.
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    db = get_supabase_client()
    today = datetime.now(IST).date().isoformat()
    
    parts = callback_data.split("_")
    if len(parts) != 3 or parts[0] != "prs":
        return
        
    question_type = parts[1] # sleep, clarity, emotion
    score_val = int(parts[2])
    
    # 1. Store the partial score in the database
    # In a real production system, we'd add columns for partial scores or use JSONB.
    # For now, we update the aggregate score.
    session_res = db.table("trader_session_state").select("prs_score").eq("trading_date", today).execute()
    current_score = session_res.data[0].get("prs_score", 0) if session_res.data else 0
    new_score = current_score + score_val
    
    db.table("trader_session_state").update({"prs_score": new_score}).eq("trading_date", today).execute()
    
    # 2. Advance the quiz by editing the message
    edit_url = f"https://api.telegram.org/bot{bot_token}/editMessageText"
    
    next_text = ""
    next_markup = {}
    
    if question_type == "sleep":
        next_text = "🧠 **Q2/3: How is your Mental Clarity?**\n(Focus, distraction level, fatigue)"
        next_markup = {
            "inline_keyboard": [
                [
                    {"text": "Sharp (3)", "callback_data": "prs_clarity_3"},
                    {"text": "Okay (2)", "callback_data": "prs_clarity_2"},
                    {"text": "Foggy (1)", "callback_data": "prs_clarity_1"}
                ]
            ]
        }
    elif question_type == "clarity":
        next_text = "❤️ **Q3/3: What is your Emotional State?**\n(Calm, tilted, stressed, euphoric)"
        next_markup = {
            "inline_keyboard": [
                [
                    {"text": "Calm & Neutral (3)", "callback_data": "prs_emotion_3"},
                    {"text": "Slightly Anxious (2)", "callback_data": "prs_emotion_2"},
                    {"text": "Tilted / Stressed (1)", "callback_data": "prs_emotion_1"}
                ]
            ]
        }
    elif question_type == "emotion":
        # Final evaluation
        db.table("trader_session_state").update({"prs_completed": True}).eq("trading_date", today).execute()
        
        # Max score is 9. Threshold is < 6 to block.
        if new_score < 6:
            db.table("trader_session_state").update({"is_trading_blocked": True}).eq("trading_date", today).execute()
            next_text = f"🛑 **PRS Score: {new_score}/9**\n\nReadiness is too low. Trading has been **BLOCKED** for today to protect capital."
        else:
            next_text = f"✅ **PRS Score: {new_score}/9**\n\nReadiness is good. Trading systems are **APPROVED** for the session."
            
        next_markup = None
        
    try:
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": next_text,
            "parse_mode": "Markdown"
        }
        if next_markup:
            payload["reply_markup"] = next_markup
            
        requests.post(edit_url, json=payload, timeout=10.0)
    except Exception as e:
        logger.error("Failed to edit PRS message: %s", e)

if __name__ == "__main__":
    send_prs_quiz()
