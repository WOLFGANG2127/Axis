"""Fail-closed Personal Readiness Score trading gate."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Any
from zoneinfo import ZoneInfo

from src.database.supabase import get_supabase_client
from src.delivery.telegram_formatter import send_telegram_alert
from src.config.settings import settings

IST = ZoneInfo("Asia/Kolkata")
PRS_CUTOFF = time(9, 10)


@dataclass(frozen=True)
class PRSGateResult:
    allowed: bool
    reason: str | None = None
    cutoff_ist: str = "09:10"
    completed_at: str | None = None


def _database(db: Any | None) -> Any:
    return db if db is not None else get_supabase_client()


def _parse_completed_at(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=IST)
    return parsed.astimezone(IST)


def _truthy(value: Any) -> bool:
    return value.strip().lower() in {"1", "true", "t", "yes", "y"} if isinstance(value, str) else bool(value)


def check_prs_trading_gate(*, db: Any | None = None, now: datetime | None = None) -> PRSGateResult:
    """Fail closed for absent, incomplete, late, or blocked PRS sessions."""
    current = (now or datetime.now(IST)).astimezone(IST)
    cutoff_dt = datetime.combine(current.date(), PRS_CUTOFF, tzinfo=IST)
    try:
        rows = _database(db).table("trader_session_state").select("prs_completed,is_trading_blocked,prs_completed_at,prs_score").eq("trading_date", current.date().isoformat()).execute().data or []
    except Exception as exc:
        return PRSGateResult(False, f"PRS_GATE_READ_FAILED: {exc}")
    if not rows:
        reason = "PRS_MISSING_AFTER_CUTOFF" if current >= cutoff_dt else "PRS_NOT_COMPLETED"
        if reason == "PRS_MISSING_AFTER_CUTOFF":
            try:
                send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, f"⚠️ PRS Gate Blocked: {reason}")
            except Exception:
                pass
        return PRSGateResult(False, reason)
    best_block_reason = "PRS_NOT_COMPLETED"
    for row in rows:
        completed_at = _parse_completed_at(row.get("prs_completed_at"))
        if not _truthy(row.get("prs_completed")):
            continue
        if _truthy(row.get("is_trading_blocked")):
            best_block_reason = "PRS_SCORE_BLOCKED"; continue
        if completed_at is None:
            best_block_reason = "PRS_COMPLETED_AT_MISSING"; continue
        if completed_at > cutoff_dt:
            best_block_reason = "PRS_COMPLETED_AFTER_CUTOFF"; continue
        return PRSGateResult(True, completed_at=completed_at.isoformat())
    
    try:
        send_telegram_alert(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, f"⚠️ PRS Gate Blocked: {best_block_reason}")
    except Exception:
        pass
    return PRSGateResult(False, best_block_reason)
