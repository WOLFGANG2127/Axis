"""Automated token lifecycle manager for Dhan API."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from src.config.settings import settings
from src.database.supabase import get_supabase_client
from src.data.dhan_client import renew_token, generate_access_token, generate_totp

async def refresh_if_needed() -> dict[str, str]:
    """Check and automatically refresh the active broker token if needed.

    Self-healing: if the broker_tokens table has no row with id=1 (fresh
    database), the function generates a new token and creates the row via
    upsert instead of raising an error.
    """
    client = get_supabase_client()
    now_utc = datetime.now(timezone.utc)

    response = client.table("broker_tokens").select("*").eq("id", 1).execute()

    # --- Self-healing path: initialise row on a fresh database -----------
    if not response.data:
        return _generate_and_upsert(client, now_utc, method_label="init")

    # --- Existing row: check expiry --------------------------------------
    row = response.data[0]
    expires_at_str = row["expires_at"]
    # Handle possible 'Z' suffix from Supabase timestamptz
    expires_at_str = expires_at_str.replace("Z", "+00:00")
    expires_at = datetime.fromisoformat(expires_at_str)

    # If expires_at is more than 2 hours away, do nothing
    if expires_at > now_utc + timedelta(hours=2):
        return {"action": "none", "status": "valid"}

    # --- Token needs refresh ----------------------------------------------
    try:
        try:
            renew_resp = renew_token()
            data = renew_resp.get("data", {})
            new_token = data.get("accessToken", data.get("access_token"))
            if not new_token:
                raise ValueError("No token found in renew_token response")
            refresh_method = "renew"
        except Exception:
            # Fallback to generate
            totp_code = generate_totp(settings.DHAN_TOTP_SECRET)
            gen_resp = generate_access_token(settings.DHAN_PIN, totp_code)
            data = gen_resp.get("data", {})
            new_token = data.get("accessToken", data.get("access_token"))
            if not new_token:
                raise ValueError("No token found in generate_access_token response")
            refresh_method = "generate"

        new_expires_at = now_utc + timedelta(hours=24)

        client.table("broker_tokens").upsert({
            "id": 1,
            "access_token": new_token,
            "generated_at": now_utc.isoformat(),
            "expires_at": new_expires_at.isoformat(),
            "refresh_method": refresh_method,
            "last_refresh_attempt": now_utc.isoformat(),
            "last_refresh_status": "ok"
        }).execute()

        return {"action": refresh_method, "status": "ok"}
    except Exception as exc:
        client.table("broker_tokens").upsert({
            "id": 1,
            "last_refresh_attempt": now_utc.isoformat(),
            "last_refresh_status": "failed"
        }).execute()
        raise RuntimeError(f"Token refresh completely failed: {exc}") from exc


def _generate_and_upsert(client, now_utc: datetime, *, method_label: str) -> dict[str, str]:
    """Generate a fresh token and upsert it as id=1 (self-healing init)."""
    try:
        try:
            renew_resp = renew_token()
            data = renew_resp.get("data", {})
            new_token = data.get("accessToken", data.get("access_token"))
            if not new_token:
                raise ValueError("No token found in renew_token response")
            refresh_method = "renew"
        except Exception:
            totp_code = generate_totp(settings.DHAN_TOTP_SECRET)
            gen_resp = generate_access_token(settings.DHAN_PIN, totp_code)
            data = gen_resp.get("data", {})
            new_token = data.get("accessToken", data.get("access_token"))
            if not new_token:
                raise ValueError("No token found in generate_access_token response")
            refresh_method = "generate"

        new_expires_at = now_utc + timedelta(hours=24)

        client.table("broker_tokens").upsert({
            "id": 1,
            "access_token": new_token,
            "generated_at": now_utc.isoformat(),
            "expires_at": new_expires_at.isoformat(),
            "refresh_method": refresh_method,
            "last_refresh_attempt": now_utc.isoformat(),
            "last_refresh_status": "ok"
        }).execute()

        return {"action": method_label, "status": "ok", "detail": f"row created via {refresh_method}"}
    except Exception as exc:
        raise RuntimeError(f"Self-healing token init failed: {exc}") from exc
