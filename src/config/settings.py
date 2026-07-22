"""Load and validate AXIS credentials at import time."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional

from pydantic import Field, HttpUrl, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_env_override = os.environ.get("AXIS_ENV_FILE")
ENV_FILE = Path(_env_override) if _env_override else PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Validated environment configuration for AXIS.

    Every field has a default so that ``settings`` can be imported safely
    in CI/CD workflows and isolated scripts without a full ``.env`` file.
    Use ``settings.require(...)`` at runtime to assert that the keys your
    code actually needs are present and non-empty.
    """

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # --- AI / LLM keys ---
    GOOGLE_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    ZAI_API_KEY: str = ""

    # --- Telegram ---
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    TELEGRAM_WEBHOOK_SECRET: str = ""

    # --- Dhan broker ---
    DHAN_CLIENT_ID: str = ""
    DHAN_ACCESS_TOKEN: str = ""
    DHAN_TOTP_SECRET: str = ""
    DHAN_PIN: str = ""

    # --- Supabase ---
    SUPABASE_URL: Optional[str] = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # --- Governance ---
    GOVERNANCE_DAILY_LOSS_MODE: str = "SHADOW"

    # --- Trading calendar ---
    AXIS_MONTHLY_EXPIRIES: str = ""

    @field_validator("TELEGRAM_CHAT_ID", mode="before")
    @classmethod
    def _coerce_telegram_chat_id(cls, value: Any) -> Any:
        if value is None:
            return value
        return str(value).strip()

    # ------------------------------------------------------------------
    # Runtime validation helpers
    # ------------------------------------------------------------------

    def require(self, *keys: str) -> None:
        """Assert that *keys* are present and non-empty.

        Call this at the top of any function / script that genuinely needs
        specific credentials, rather than relying on import-time checks.

        Example::

            settings.require("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")
        """
        missing: list[str] = []
        for key in keys:
            if not hasattr(self, key):
                missing.append(key)
                continue
            value = getattr(self, key)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(key)
        if missing:
            raise ValueError(
                "Missing or empty required settings: " + ", ".join(missing)
            )

    # Keep legacy alias so existing callers still work.
    validate_for = require


def _load_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        details = [
            f"{err['loc'][0]}: {err['msg']}"
            for err in exc.errors()
            if err.get("loc")
        ]
        message = "AXIS settings validation failed at import"
        if details:
            message += " - " + "; ".join(str(item) for item in details)
        raise RuntimeError(message) from exc


settings = _load_settings()
