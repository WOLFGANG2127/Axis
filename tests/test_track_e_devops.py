"""Track E deployment/CI/CD contract tests."""

from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path

import pytest


def test_main_pipeline_workflow_is_centralized_sequential_and_not_matrix():
    workflow = Path(".github/workflows/main_pipeline.yml").read_text(encoding="utf-8")

    assert "strategy:" not in workflow
    assert "matrix:" not in workflow
    assert "python main.py --all" in workflow
    assert "cancel-in-progress: false" in workflow
    assert "cron: '*/5 3-10 * * *'" in workflow


def test_main_pipeline_references_required_backend_secrets():
    workflow = Path(".github/workflows/main_pipeline.yml").read_text(encoding="utf-8")
    required = [
        "GOOGLE_API_KEY",
        "GROQ_API_KEY",
        "ZAI_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
        "TELEGRAM_WEBHOOK_SECRET",
        "DHAN_CLIENT_ID",
        "DHAN_ACCESS_TOKEN",
        "DHAN_TOTP_SECRET",
        "DHAN_PIN",
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
    ]

    for secret in required:
        assert f"${{{{ secrets.{secret} }}}}" in workflow


def test_settings_fail_loudly_when_webhook_secret_missing(monkeypatch):
    for key, value in {
        "GOOGLE_API_KEY": "google",
        "GROQ_API_KEY": "groq",
        "ZAI_API_KEY": "zai",
        "TELEGRAM_BOT_TOKEN": "token",
        "TELEGRAM_CHAT_ID": "123",
        "DHAN_CLIENT_ID": "dhan",
        "DHAN_ACCESS_TOKEN": "dhan-token",
        "DHAN_TOTP_SECRET": "totp",
        "DHAN_PIN": "1234",
        "SUPABASE_URL": "https://example.supabase.co",
        "SUPABASE_ANON_KEY": "anon",
        "SUPABASE_SERVICE_ROLE_KEY": "service",
    }.items():
        monkeypatch.setenv(key, value)
    monkeypatch.delenv("TELEGRAM_WEBHOOK_SECRET", raising=False)
    sys.modules.pop("src.config.settings", None)

    with pytest.raises(RuntimeError, match="TELEGRAM_WEBHOOK_SECRET"):
        importlib.import_module("src.config.settings")

    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "test-webhook-secret")
    sys.modules.pop("src.config.settings", None)
    importlib.import_module("src.config.settings")

def test_main_cli_sends_pipeline_crashed_alert_before_reraising(monkeypatch):
    import main
    from src.config.settings import settings
    from src.delivery import telegram_formatter

    alerts = []

    async def failing_main():
        raise RuntimeError("synthetic crash")

    monkeypatch.setattr(main, "_amain", failing_main)
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "token", raising=False)
    monkeypatch.setattr(settings, "TELEGRAM_CHAT_ID", "chat", raising=False)
    monkeypatch.setattr(
        telegram_formatter,
        "send_telegram_alert",
        lambda _token, _chat, message: alerts.append(message) or True,
    )

    with pytest.raises(RuntimeError, match="synthetic crash"):
        main._run_cli()

    assert alerts
    assert "AXIS PIPELINE CRASHED" in alerts[-1]
    assert "synthetic crash" in alerts[-1]


def test_all_non_raw_telegram_paths_use_shared_queue_after_track_a():
    paths = [
        Path("src/delivery/interactive_ui.py"),
        Path("src/scheduling/prs_quiz.py"),
        Path("netlify/functions/telegram_webhook.py"),
    ]

    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "send_telegram_payload" in text
        assert "requests.post" not in text



