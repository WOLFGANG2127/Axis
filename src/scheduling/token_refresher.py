"""Automated token lifecycle manager for Dhan API."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from src.config.settings import settings
from src.database.supabase import get_supabase_client
from src.data.dhan_client import renew_token, generate_access_token, generate_totp

async def refresh_if_needed() -> dict[str, str]:
    """Check and automatically refresh the active broker token if needed."""
    client = get_supabase_client()
    response = client.table("broker_tokens").select("*").eq("id", 1).execute()
    
    if not response.data:
        raise RuntimeError("broker_tokens table missing row id=1")
    
    row = response.data[0]
    expires_at_str = row["expires_at"]
    # Handle possible 'Z' suffix from Supabase timestamptz
    expires_at_str = expires_at_str.replace("Z", "+00:00")
    expires_at = datetime.fromisoformat(expires_at_str)

    # Note: timezone boundary rule applied here. UTC specifically to compare against expires_at
    now_utc = datetime.now(timezone.utc)
    
    # If expires_at is more than 2 hours away, do nothing
    if expires_at > now_utc + timedelta(hours=2):
        return {"action": "none", "status": "valid"}

    # Need to refresh
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
        
        client.table("broker_tokens").update({
            "access_token": new_token,
            "generated_at": now_utc.isoformat(),
            "expires_at": new_expires_at.isoformat(),
            "refresh_method": refresh_method,
            "last_refresh_attempt": now_utc.isoformat(),
            "last_refresh_status": "ok"
        }).eq("id", 1).execute()
        
        return {"action": refresh_method, "status": "ok"}
    except Exception as exc:
        client.table("broker_tokens").update({
            "last_refresh_attempt": now_utc.isoformat(),
            "last_refresh_status": "failed"
        }).eq("id", 1).execute()
        raise RuntimeError(f"Token refresh completely failed: {exc}") from exc
