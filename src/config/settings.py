"""Load and validate AXIS credentials at import time."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic import Field, HttpUrl, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_env_override = os.environ.get("AXIS_ENV_FILE")
ENV_FILE = Path(_env_override) if _env_override else PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Validated environment configuration for AXIS."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    GOOGLE_API_KEY: str = Field(min_length=1)
    GROQ_API_KEY: str = Field(min_length=1)
    ZAI_API_KEY: str = Field(min_length=1)
    TELEGRAM_BOT_TOKEN: str = Field(min_length=1)
    TELEGRAM_CHAT_ID: str = Field(min_length=1)
    TELEGRAM_WEBHOOK_SECRET: str = Field(min_length=1)
    DHAN_CLIENT_ID: str = Field(min_length=1)
    DHAN_ACCESS_TOKEN: str = Field(min_length=1)
    DHAN_TOTP_SECRET: str = Field(min_length=1)
    DHAN_PIN: str = Field(min_length=1)
    SUPABASE_URL: HttpUrl
    SUPABASE_ANON_KEY: str = Field(min_length=1)
    SUPABASE_SERVICE_ROLE_KEY: str = Field(min_length=1)
    
    GOVERNANCE_DAILY_LOSS_MODE: str = "SHADOW"

    @field_validator("TELEGRAM_CHAT_ID", mode="before")
    @classmethod
    def _coerce_telegram_chat_id(cls, value: Any) -> Any:
        if value is None:
            return value
        return str(value).strip()

    @field_validator("DHAN_ACCESS_TOKEN", mode="before")
    @classmethod
    def _mock_dhan_access_token(cls, value: Any) -> Any:
        if not value or (isinstance(value, str) and not value.strip()):
            return "MOCK_TOKEN_FOR_REFRESH"
        return value

    def validate_for(self, *keys: str) -> None:
        """Ensure the named settings exist and are non-empty."""
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

