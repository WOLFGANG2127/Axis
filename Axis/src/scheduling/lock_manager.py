"""Run-level locking for one AXIS symbol cycle."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

IST = ZoneInfo("Asia/Kolkata")
_LOCAL_LOCKS: dict[str, datetime] = {}


def _lock_id(symbol: str) -> str:
    return f"axis_cycle_{symbol.strip().upper()}"


def get_lock_db() -> Any | None:
    """Return a Supabase client without importing global settings validation."""

    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return None
    try:
        from supabase import create_client

        return create_client(url.rstrip("/"), key)
    except Exception:
        return None


def _execute_data(query: Any) -> list[dict[str, Any]]:
    return query.execute().data or []


def _local_acquire(lock_id: str, expires_at: datetime) -> bool:
    current = _LOCAL_LOCKS.get(lock_id)
    if current and current > datetime.now(IST):
        return False
    _LOCAL_LOCKS[lock_id] = expires_at
    return True


def _local_release(lock_id: str) -> None:
    _LOCAL_LOCKS.pop(lock_id, None)


def acquire_run_lock(
    symbol: str,
    *,
    ttl_seconds: int = 240,
    db: Any | None = None,
    now: datetime | None = None,
) -> bool:
    """Acquire the per-symbol run lock."""

    local_now = (now or datetime.now(IST)).astimezone(IST)
    expires_at = local_now + timedelta(seconds=ttl_seconds)
    lock_id = _lock_id(symbol)
    database = db if db is not None else get_lock_db()
    if database is None:
        return _local_acquire(lock_id, expires_at)

    try:
        rows = _execute_data(
            database.table("run_locks")
            .select("lock_id,expires_at")
            .eq("lock_id", lock_id)
            .limit(1)
        )
        if rows:
            expires_raw = rows[0].get("expires_at")
            if expires_raw:
                active_until = datetime.fromisoformat(str(expires_raw).replace("Z", "+00:00"))
                if active_until.astimezone(IST) > local_now:
                    return False
        database.table("run_locks").upsert(
            {
                "lock_id": lock_id,
                "symbol": symbol.strip().upper(),
                "acquired_at": local_now.isoformat(),
                "expires_at": expires_at.isoformat(),
            },
            on_conflict="lock_id",
        ).execute()
        return True
    except Exception:
        return _local_acquire(lock_id, expires_at)


def release_run_lock(symbol: str, *, db: Any | None = None) -> None:
    """Release the per-symbol run lock. Safe to call from ``finally``."""

    lock_id = _lock_id(symbol)
    database = db if db is not None else get_lock_db()
    if database is None:
        _local_release(lock_id)
        return
    try:
        now = datetime.now(IST).isoformat()
        database.table("run_locks").update(
            {"released_at": now, "expires_at": now}
        ).eq("lock_id", lock_id).execute()
    except Exception:
        _local_release(lock_id)
