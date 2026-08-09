"""Inbound Telegram command router and handlers for AXIS.

Supported commands:
- /ready: UPSERT trader_session_state for today with is_ready = true (D-004)
- /resend: Retry latest unsent signal where telegram_sent = false (D-048)
- /close: Delete row from active_position for given symbol or all positions (D-050)
- /record: Honest stub returning explicit 'not yet implemented' alert
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from src.config.settings import settings
from src.database.supabase import get_supabase_client
from src.delivery.telegram_formatter import send_telegram_alert

logger = logging.getLogger("axis.commands")
IST = ZoneInfo("Asia/Kolkata")


def parse_telegram_update(update: dict[str, Any]) -> tuple[str, str, str]:
    """Extract (command, args, chat_id) from incoming Telegram update payload."""
    message = update.get("message") or update.get("edited_message") or {}
    text = (message.get("text") or "").strip()
    chat_id = str(message.get("chat", {}).get("id") or settings.TELEGRAM_CHAT_ID)

    if not text.startswith("/"):
        return "", "", chat_id

    parts = text.split(maxsplit=1)
    raw_cmd = parts[0].lower()
    # Strip bot username if present, e.g. /ready@my_bot -> /ready
    command = raw_cmd.split("@")[0]
    args = parts[1].strip() if len(parts) > 1 else ""

    return command, args, chat_id


def handle_ready_command(chat_id: str, db: Any = None) -> None:
    """UPSERT trader_session_state row for today with is_ready = true (D-004)."""
    if db is None:
        db = get_supabase_client()

    today_str = datetime.now(IST).date().isoformat()
    now_iso = datetime.now(IST).isoformat()

    try:
        db.table("trader_session_state").upsert(
            {
                "session_date": today_str,
                "is_ready": True,
                "updated_at": now_iso,
            },
            on_conflict="session_date",
        ).execute()

        msg = f"✅ Trader session state set to READY for {today_str}."
        logger.info(msg)
        if chat_id and settings.TELEGRAM_BOT_TOKEN:
            send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, chat_id, msg)
    except Exception as e:
        logger.error("Failed to execute /ready command: %s", e)
        if chat_id and settings.TELEGRAM_BOT_TOKEN:
            send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, chat_id, f"❌ Failed to set READY state: {e}")


def handle_resend_command(chat_id: str, db: Any = None) -> None:
    """Retry latest unsent signal where telegram_sent = false (D-048)."""
    if db is None:
        db = get_supabase_client()

    try:
        res = (
            db.table("signals")
            .select("*")
            .eq("telegram_sent", False)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        unsent_signals = res.data or []

        if not unsent_signals:
            msg = "ℹ️ No unsent signals to retry."
            logger.info(msg)
            if chat_id and settings.TELEGRAM_BOT_TOKEN:
                send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, chat_id, msg)
            return

        sig = unsent_signals[0]
        sig_id = sig["id"]
        symbol = sig.get("symbol", "UNKNOWN")

        alert_text = (
            f"🚨 RESENT SIGNAL: {symbol}\n"
            f"Direction Score: {sig.get('direction_score')}\n"
            f"Strategy: {sig.get('active_strategy_slug', 'N/A')}\n"
            f"Cycle Timestamp: {sig.get('cycle_timestamp')}"
        )

        success = False
        if chat_id and settings.TELEGRAM_BOT_TOKEN:
            success = send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, chat_id, alert_text)

        if success:
            db.table("signals").update(
                {"telegram_sent": True, "telegram_error": None}
            ).eq("id", sig_id).execute()
            send_telegram_alert(
                settings.TELEGRAM_BOT_TOKEN, chat_id, f"✅ Signal {symbol} resent successfully."
            )
            logger.info("Successfully resent signal %s for %s", sig_id, symbol)
        else:
            err_msg = "Telegram delivery failed"
            db.table("signals").update(
                {"telegram_sent": False, "telegram_error": err_msg}
            ).eq("id", sig_id).execute()
            if chat_id and settings.TELEGRAM_BOT_TOKEN:
                send_telegram_alert(
                    settings.TELEGRAM_BOT_TOKEN, chat_id, f"❌ Failed to resend signal for {symbol}."
                )
            logger.error("Failed to resend signal %s for %s", sig_id, symbol)

    except Exception as e:
        logger.error("Error in /resend handler: %s", e)
        if chat_id and settings.TELEGRAM_BOT_TOKEN:
            send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, chat_id, f"❌ Error retrying signal: {e}")


def handle_close_command(args: str, chat_id: str, db: Any = None) -> None:
    """Delete row from active_position for given symbol or clear all positions (D-050)."""
    if db is None:
        db = get_supabase_client()

    target_symbol = args.strip().upper()

    try:
        if target_symbol:
            db.table("active_position").delete().eq("symbol", target_symbol).execute()
            msg = f"✅ Position closed for {target_symbol} (removed from active_position)."
        else:
            db.table("active_position").delete().neq("symbol", "").execute()
            msg = "✅ All active positions closed (cleared active_position)."

        logger.info(msg)
        if chat_id and settings.TELEGRAM_BOT_TOKEN:
            send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, chat_id, msg)

    except Exception as e:
        logger.error("Failed to execute /close command: %s", e)
        if chat_id and settings.TELEGRAM_BOT_TOKEN:
            send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, chat_id, f"❌ Failed to close position: {e}")


def handle_record_stub(chat_id: str) -> None:
    """Honest stub for /record returning explicit 'not yet implemented' message."""
    msg = "⚠️ /record full pipeline is not yet implemented."
    logger.info("Handled /record command stub.")
    if chat_id and settings.TELEGRAM_BOT_TOKEN:
        send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, chat_id, msg)


def dispatch_telegram_command(update: dict[str, Any], db: Any = None) -> None:
    """Parse update and dispatch to appropriate command handler."""
    command, args, chat_id = parse_telegram_update(update)

    if not command:
        return

    logger.info("Dispatching command '%s' with args '%s' for chat_id '%s'", command, args, chat_id)

    if command == "/ready":
        handle_ready_command(chat_id, db=db)
    elif command == "/resend":
        handle_resend_command(chat_id, db=db)
    elif command == "/close":
        handle_close_command(args, chat_id, db=db)
    elif command == "/record":
        handle_record_stub(chat_id)
    else:
        logger.info("Unrecognized command '%s' ignored.", command)
