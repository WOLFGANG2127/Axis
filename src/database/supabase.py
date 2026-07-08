"""Lazy Supabase service-role client for trusted local pipeline writes."""

from __future__ import annotations

from functools import lru_cache
from typing import Any


@lru_cache(maxsize=1)
def get_supabase_client() -> Any:
    """Create the privileged client only when a database operation is used."""
    from supabase import create_client

    from src.config.settings import settings

    return create_client(
        str(settings.SUPABASE_URL).rstrip("/"),
        settings.SUPABASE_SERVICE_ROLE_KEY,
    )
