"""Telegram MarkdownV2 formatting and safe delivery."""

from __future__ import annotations

from typing import Any

import requests

MARKDOWN_V2_SPECIALS = r"_*[]()~`>#+-=|{}.!"


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

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "MarkdownV2",
                "disable_web_page_preview": True,
            },
            timeout=timeout,
        )
        response.raise_for_status()
        return True
    except Exception:
        try:
            fallback = requests.post(
                url,
                json={"chat_id": chat_id, "text": str(text), "disable_web_page_preview": True},
                timeout=timeout,
            )
            fallback.raise_for_status()
            return True
        except Exception:
            return False
