"""Personal Readiness Score (PRS) Module."""

from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from src.config.settings import settings
from src.database.supabase import get_supabase_client
from src.delivery.telegram_formatter import sanitize_telegram_md, send_telegram_payload

logger = logging.getLogger("axis.prs")
IST = ZoneInfo("Asia/Kolkata")


def _markdown_payload(*, chat_id: str, text: str, reply_markup: dict | None = None, message_id: int | None = None) -> dict:
    payload = {
        "chat_id": chat_id,
        "text": sanitize_telegram_md(text.replace("**", "")),
        "parse_mode": "MarkdownV2",
    }
    if message_id is not None:
        payload["message_id"] = message_id
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return payload


def _plain_payload(*, chat_id: str, text: str, reply_markup: dict | None = None, message_id: int | None = None) -> dict:
    payload = {"chat_id": chat_id, "text": text.replace("**", "")}
    if message_id is not None:
        payload["message_id"] = message_id
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return payload


def send_prs_quiz() -> None:
    """Send the Morning Readiness Quiz via Telegram inline keyboard."""

    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    text = (
        "?? **Morning Personal Readiness Score (PRS)**\n\n"
        "Let's assess your readiness to trade today.\n"
        "**Q1/3: How was your Sleep Quality?**"
    )
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "Excellent (3)", "callback_data": "prs_sleep_3"},
                {"text": "Average (2)", "callback_data": "prs_sleep_2"},
                {"text": "Poor (1)", "callback_data": "prs_sleep_1"},
            ]
        ]
    }

    try:
        sent = send_telegram_payload(
            bot_token,
            "sendMessage",
            _markdown_payload(chat_id=chat_id, text=text, reply_markup=reply_markup),
            timeout=10.0,
        )
        if not sent:
            send_telegram_payload(
                bot_token,
                "sendMessage",
                _plain_payload(chat_id=chat_id, text=text, reply_markup=reply_markup),
                timeout=10.0,
            )
        logger.info("Successfully dispatched PRS Quiz (Q1).")

        db = get_supabase_client()
        today = datetime.now(IST).date().isoformat()
        existing = db.table("trader_session_state").select("id").eq("trading_date", today).execute()
        if not existing.data:
            db.table("trader_session_state").insert(
                {
                    "trading_date": today,
                    "is_trading_blocked": False,
                    "prs_score": 0,
                    "prs_completed": False,
                    "prs_completed_at": None,
                    "prs_block_reason": None,
                }
            ).execute()
    except Exception as exc:
        logger.error("Failed to send PRS Quiz: %s", exc)


def process_prs_callback(callback_data: str, message_id: int) -> None:
    """Process PRS answers, advance the quiz, and update trader state."""

    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    db = get_supabase_client()
    today = datetime.now(IST).date().isoformat()

    parts = callback_data.split("_")
    if len(parts) != 3 or parts[0] != "prs":
        return

    question_type = parts[1]
    score_val = int(parts[2])

    session_res = db.table("trader_session_state").select("prs_score").eq("trading_date", today).execute()
    current_score = session_res.data[0].get("prs_score", 0) if session_res.data else 0
    new_score = current_score + score_val
    db.table("trader_session_state").update({"prs_score": new_score}).eq("trading_date", today).execute()

    next_text = ""
    next_markup = None

    if question_type == "sleep":
        next_text = "?? **Q2/3: How is your Mental Clarity?**\n(Focus, distraction level, fatigue)"
        next_markup = {
            "inline_keyboard": [
                [
                    {"text": "Sharp (3)", "callback_data": "prs_clarity_3"},
                    {"text": "Okay (2)", "callback_data": "prs_clarity_2"},
                    {"text": "Foggy (1)", "callback_data": "prs_clarity_1"},
                ]
            ]
        }
    elif question_type == "clarity":
        next_text = "?? **Q3/3: What is your Emotional State?**\n(Calm, tilted, stressed, euphoric)"
        next_markup = {
            "inline_keyboard": [
                [
                    {"text": "Calm & Neutral (3)", "callback_data": "prs_emotion_3"},
                    {"text": "Slightly Anxious (2)", "callback_data": "prs_emotion_2"},
                    {"text": "Tilted / Stressed (1)", "callback_data": "prs_emotion_1"},
                ]
            ]
        }
    elif question_type == "emotion":
        completed_at = datetime.now(IST).isoformat()
        if new_score < 6:
            db.table("trader_session_state").update(
                {
                    "prs_completed": True,
                    "prs_completed_at": completed_at,
                    "is_trading_blocked": True,
                    "prs_block_reason": "PRS_SCORE_BLOCKED",
                }
            ).eq("trading_date", today).execute()
            next_text = f"?? **PRS Score: {new_score}/9**\n\nReadiness is too low. Trading has been **BLOCKED** for today to protect capital."
        else:
            db.table("trader_session_state").update(
                {
                    "prs_completed": True,
                    "prs_completed_at": completed_at,
                    "is_trading_blocked": False,
                    "prs_block_reason": None,
                }
            ).eq("trading_date", today).execute()
            next_text = f"? **PRS Score: {new_score}/9**\n\nReadiness is good. Trading systems are **APPROVED** for the session."
    else:
        return

    try:
        sent = send_telegram_payload(
            bot_token,
            "editMessageText",
            _markdown_payload(chat_id=chat_id, message_id=message_id, text=next_text, reply_markup=next_markup),
            timeout=10.0,
        )
        if not sent:
            send_telegram_payload(
                bot_token,
                "editMessageText",
                _plain_payload(chat_id=chat_id, message_id=message_id, text=next_text, reply_markup=next_markup),
                timeout=10.0,
            )
    except Exception as exc:
        logger.error("Failed to edit PRS message: %s", exc)


if __name__ == "__main__":
    send_prs_quiz()
