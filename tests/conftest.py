"""Offline test environment bootstrap.

Unit tests must not require real credentials, but settings validation should
still fail loudly in production when a key is absent. These harmless fake values
keep imports deterministic unless a test deliberately overrides them.
"""

from __future__ import annotations

import os


for _key, _value in {
    "GOOGLE_API_KEY": "test-google",
    "GROQ_API_KEY": "test-groq",
    "ZAI_API_KEY": "test-zai",
    "TELEGRAM_BOT_TOKEN": "123:test",
    "TELEGRAM_CHAT_ID": "-100123",
    "TELEGRAM_WEBHOOK_SECRET": "test-webhook-secret",
    "DHAN_CLIENT_ID": "123456",
    "DHAN_ACCESS_TOKEN": "test-token",
    "DHAN_TOTP_SECRET": "test-totp",
    "DHAN_PIN": "1234",
    "SUPABASE_URL": "https://example.supabase.co",
    "SUPABASE_ANON_KEY": "test-anon",
    "SUPABASE_SERVICE_ROLE_KEY": "test-service",
}.items():
    os.environ.setdefault(_key, _value)

