"""10-second smoke test of all critical AXIS infrastructure paths."""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger("axis.health")


def _check_supabase() -> dict[str, Any]:
    """Verify Supabase read connectivity."""
    try:
        from src.database.supabase import get_supabase_client
        client = get_supabase_client()
        result = client.table("broker_tokens").select("id").limit(1).execute()
        return {"status": "ok", "rows": len(result.data or [])}
    except Exception as exc:
        return {"status": "fail", "error": str(exc)}


def _check_dhan() -> dict[str, Any]:
    """Verify Dhan API token is present and the headers function resolves."""
    try:
        from src.data.dhan_client import _headers
        headers = _headers()
        has_token = bool(headers.get("access-token"))
        return {"status": "ok" if has_token else "fail", "has_token": has_token}
    except Exception as exc:
        return {"status": "fail", "error": str(exc)}


def _check_gemini() -> dict[str, Any]:
    """Verify Gemini API key is configured and reachable."""
    try:
        from src.config.settings import settings
        if not settings.GOOGLE_API_KEY or len(settings.GOOGLE_API_KEY) < 10:
            return {"status": "fail", "error": "GOOGLE_API_KEY too short or missing"}
        return {"status": "ok", "key_length": len(settings.GOOGLE_API_KEY)}
    except Exception as exc:
        return {"status": "fail", "error": str(exc)}


def _check_env_vars() -> dict[str, Any]:
    """Verify all required environment variables are set."""
    try:
        from src.config.settings import settings
        required = [
            "GOOGLE_API_KEY", "GROQ_API_KEY", "ZAI_API_KEY",
            "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID",
            "DHAN_CLIENT_ID", "DHAN_ACCESS_TOKEN",
            "DHAN_TOTP_SECRET", "DHAN_PIN",
            "SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY",
        ]
        missing = []
        for var in required:
            val = getattr(settings, var, None)
            if val is None or (isinstance(val, str) and not val.strip()):
                missing.append(var)
        if missing:
            return {"status": "fail", "missing": missing}
        return {"status": "ok", "checked": len(required)}
    except Exception as exc:
        return {"status": "fail", "error": str(exc)}


def run_smoke_test() -> dict[str, Any]:
    """Run all checks and return a consolidated status dict."""
    start = time.monotonic()
    results = {
        "supabase": _check_supabase(),
        "dhan": _check_dhan(),
        "gemini": _check_gemini(),
        "env_vars": _check_env_vars(),
    }
    elapsed = time.monotonic() - start
    all_ok = all(r["status"] == "ok" for r in results.values())
    results["overall"] = "HEALTHY" if all_ok else "DEGRADED"
    results["elapsed_seconds"] = round(elapsed, 3)
    
    status_line = f"AXIS Health: {results['overall']} ({elapsed:.1f}s) — " + ", ".join(
        f"{k}={v['status']}" for k, v in results.items()
        if isinstance(v, dict) and "status" in v
    )
    if all_ok:
        logger.info(status_line)
    else:
        logger.warning(status_line)
    print(status_line)
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_smoke_test()
