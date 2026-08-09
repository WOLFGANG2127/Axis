"""Render deployment server for AXIS backend services and Telegram webhook."""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from src.commands.router import dispatch_telegram_command, parse_telegram_update
from src.config.settings import settings
from src.database.supabase import get_supabase_client

logger = logging.getLogger("axis.server")

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


@app.get("/")
def home() -> dict[str, str]:
    return {"status": "AXIS backend pipeline is actively executing in the background."}


@app.head("/api/health")
@app.get("/api/health")
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/telegram/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(None),
) -> JSONResponse:
    """Inbound Telegram webhook route (D-055).

    Validates secret token, checks update_id dedup against telegram_updates_processed,
    dispatches command handlers, and returns 200 OK.
    """
    expected_secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET") or settings.TELEGRAM_WEBHOOK_SECRET
    if not expected_secret or x_telegram_bot_api_secret_token != expected_secret:
        logger.warning("Unauthorized webhook access attempt.")
        raise HTTPException(status_code=401, detail="Invalid secret token")

    try:
        payload: dict[str, Any] = await request.json()
    except Exception:
        logger.error("Invalid JSON payload received in telegram_webhook.")
        return JSONResponse(content={"status": "invalid_json"}, status_code=200)

    update_id = payload.get("update_id")
    if update_id is not None:
        try:
            db = get_supabase_client()
            res = (
                db.table("telegram_updates_processed")
                .select("update_id")
                .eq("update_id", update_id)
                .execute()
            )
            if res.data:
                logger.info("Duplicate update_id %s received; skipping.", update_id)
                return JSONResponse(content={"status": "already_processed"}, status_code=200)

            command, _, _ = parse_telegram_update(payload)
            db.table("telegram_updates_processed").insert(
                {"update_id": update_id, "command": command or None}
            ).execute()
        except Exception as exc:
            logger.error("Error during update_id dedup check: %s", exc)

    try:
        dispatch_telegram_command(payload)
    except Exception as exc:
        logger.error("Error dispatching telegram command: %s", exc)

    return JSONResponse(content={"status": "ok"}, status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=10000, workers=1)