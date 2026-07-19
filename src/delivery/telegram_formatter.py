"""Telegram MarkdownV2 formatting and safe delivery."""

from __future__ import annotations

import threading
import time
from typing import Any

import requests

MARKDOWN_V2_SPECIALS = r"_*[]()~`>#+-=|{}.!"
TELEGRAM_SEND_INTERVAL_SECONDS = 1.05
_QUEUE_LOCK = threading.Lock()
_LAST_SEND_TS = 0.0


def reset_telegram_queue_for_tests() -> None:
    global _LAST_SEND_TS
    with _QUEUE_LOCK:
        _LAST_SEND_TS = 0.0


def _rate_limited_post(url: str, *, json: dict[str, Any], timeout: float) -> requests.Response:
    global _LAST_SEND_TS
    with _QUEUE_LOCK:
        now = time.monotonic()
        wait = TELEGRAM_SEND_INTERVAL_SECONDS - (now - _LAST_SEND_TS)
        if wait > 0:
            time.sleep(wait)
        response = requests.post(url, json=json, timeout=timeout)
        _LAST_SEND_TS = time.monotonic()
        return response


def send_telegram_payload(
    bot_token: str,
    method: str,
    payload: dict[str, Any],
    *,
    timeout: float = 10.0,
) -> bool:
    """Queue one Telegram API payload and return False on API/network failure."""

    url = f"https://api.telegram.org/bot{bot_token}/{method}"
    try:
        response = _rate_limited_post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        return True
    except Exception:
        return False


def sanitize_telegram_md(text: Any) -> str:
    """Escape every Telegram MarkdownV2 special character."""

    raw = str(text).replace("\\", "\\\\")
    return "".join(f"\\{char}" if char in MARKDOWN_V2_SPECIALS else char for char in raw)


def send_telegram_alert(
    bot_token: str,
    chat_id: str,
    text: str,
    *,
    timeout: float = 10.0,
) -> bool:
    """Send a Telegram message, returning False on any API/network failure."""

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True,
    }
    if send_telegram_payload(bot_token, "sendMessage", payload, timeout=timeout):
        return True
    fallback = {"chat_id": chat_id, "text": str(text), "disable_web_page_preview": True}
    return send_telegram_payload(bot_token, "sendMessage", fallback, timeout=timeout)


def send_behavioral_rating_prompt(
    bot_token: str,
    chat_id: str,
    trade_id: Any,
    *,
    timeout: float = 10.0,
) -> bool:
    """Send an outbound Telegram message asking the user to rate their Session Quality/Behavior."""

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "5 - Perfect Execution", "callback_data": f"rate_{trade_id}_5"},
                {"text": "4 - Good", "callback_data": f"rate_{trade_id}_4"},
            ],
            [
                {"text": "3 - Average", "callback_data": f"rate_{trade_id}_3"},
                {"text": "2 - Poor", "callback_data": f"rate_{trade_id}_2"},
            ],
            [
                {"text": "1 - Tilt / Reckless", "callback_data": f"rate_{trade_id}_1"},
            ],
        ]
    }

    raw_text = (
        f"Trade {trade_id} Closed\n\n"
        "Please rate your behavioral execution for this trade. "
        "Your honest input trains the regime-shift decay model."
    )
    escaped_text = sanitize_telegram_md(raw_text)

    payload = {
        "chat_id": chat_id,
        "text": f"BEHAVIOR CHECK: {escaped_text}",
        "parse_mode": "MarkdownV2",
        "reply_markup": reply_markup,
    }
    if send_telegram_payload(bot_token, "sendMessage", payload, timeout=timeout):
        return True
    fallback = {
        "chat_id": chat_id,
        "text": f"BEHAVIOR CHECK: {raw_text}",
        "reply_markup": reply_markup,
    }
    return send_telegram_payload(bot_token, "sendMessage", fallback, timeout=timeout)
