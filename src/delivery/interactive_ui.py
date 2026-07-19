"""Interactive UI components for Telegram."""

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from src.config.settings import settings
from src.delivery.telegram_formatter import sanitize_telegram_md, send_telegram_payload

logger = logging.getLogger("axis.ui")
IST = ZoneInfo("Asia/Kolkata")

def send_cooling_off_ui(cooling_off_until_iso: str) -> bool:
    """
    Send an interactive Telegram message when a circuit breaker hits,
    showing the countdown and an override button.
    """
    bot_token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    try:
        dt = datetime.fromisoformat(cooling_off_until_iso.replace("Z", "+00:00")).astimezone(IST)
        time_str = dt.strftime("%I:%M %p IST")
    except Exception:
        time_str = cooling_off_until_iso

    raw_text = (
        "CIRCUIT BREAKER ENGAGED\n\n"
        "Trading has been suspended to protect capital.\n"
        f"Cooling-Off Period Until: {time_str}\n\n"
        "You may manually override this lock, but doing so bypasses structural safety gates."
    )
    text = sanitize_telegram_md(raw_text)
    
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "⚠️ YES, I ACCEPT THE RISK", "callback_data": "override_cooling_off"}
            ]
        ]
    }
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2",
        "reply_markup": reply_markup,
    }
    sent = send_telegram_payload(bot_token, "sendMessage", payload, timeout=10.0)
    if not sent:
        logger.error("Failed to send Cooling-Off UI")
    return sent
