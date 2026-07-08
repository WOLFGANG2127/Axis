"""Postgres-backed distributed lock facade for serialized external LLM calls."""

from __future__ import annotations

import asyncio
import uuid
from src.database.supabase import get_supabase_client

# Unique identifier for this worker/process to safely release its own locks
_WORKER_ID = str(uuid.uuid4())

def _sync_acquire(lock_id: str, ttl_seconds: int) -> bool:
    client = get_supabase_client()
    try:
        response = client.rpc("acquire_infrastructure_lock", {
            "p_lock_id": lock_id,
            "p_acquired_by": _WORKER_ID,
            "p_ttl_seconds": ttl_seconds
        }).execute()
        return bool(response.data)
    except Exception as e:
        print(f"Warning: Failed to acquire distributed lock '{lock_id}': {e}")
        return False

def _sync_release(lock_id: str) -> None:
    client = get_supabase_client()
    try:
        client.rpc("release_infrastructure_lock", {
            "p_lock_id": lock_id,
            "p_acquired_by": _WORKER_ID
        }).execute()
    except Exception as e:
        print(f"Warning: Failed to release distributed lock '{lock_id}': {e}")

async def acquire(lock_id: str, ttl_seconds: int = 60) -> bool:
    """Acquire a Postgres-backed infrastructure lock.

    Self-healing acquisition uses an RPC that executes:
    INSERT ... ON CONFLICT DO UPDATE ... WHERE expires_at < now()
    """
    return await asyncio.to_thread(_sync_acquire, lock_id, ttl_seconds)

async def release(lock_id: str) -> None:
    """Release a Postgres-backed infrastructure lock if held by this worker."""
    await asyncio.to_thread(_sync_release, lock_id)
