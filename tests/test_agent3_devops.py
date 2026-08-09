"""Comprehensive contract and functionality tests for Agent 3 DevOps tasks:
D-010, D-051, D-055, D-004, D-048, and D-050.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from server import app
from src.commands.router import (
    dispatch_telegram_command,
    handle_close_command,
    handle_ready_command,
    handle_record_stub,
    handle_resend_command,
    parse_telegram_update,
)
from src.config.settings import settings
from src.scheduling.no_trade_summary import run_no_trade_summary

client = TestClient(app)


def test_procfile_points_to_server_app():
    procfile_text = Path("Procfile").read_text(encoding="utf-8")
    assert "web: uvicorn server:app --host 0.0.0.0 --port 10000" in procfile_text.strip()


def test_render_free_tier_mandates_in_server_py():
    server_code = Path("server.py").read_text(encoding="utf-8")
    # a. FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    assert "FastAPI(docs_url=None, redoc_url=None, openapi_url=None)" in server_code
    # b. uvicorn.run() uses workers=1, no threads=
    assert "workers=1" in server_code
    assert "threads=" not in server_code
    # c. Never use BackgroundTasks
    assert "BackgroundTasks" not in server_code
    # d. No rogue background subprocess at import time
    assert "subprocess.Popen" not in server_code


def test_github_actions_concurrency_and_timeout(monkeypatch):
    workflow_text = Path(".github/workflows/main_pipeline.yml").read_text(encoding="utf-8")
    assert "run-cycle:" in workflow_text
    assert "timeout-minutes: 5" in workflow_text
    assert "group: axis-trading-cycle" in workflow_text
    assert "cancel-in-progress: false" in workflow_text


def test_webhook_returns_401_on_missing_or_invalid_secret(monkeypatch):
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "valid-secret-token")
    monkeypatch.setattr(settings, "TELEGRAM_WEBHOOK_SECRET", "valid-secret-token")

    # Missing header
    res1 = client.post("/telegram/webhook", json={"update_id": 100})
    assert res1.status_code == 401

    # Invalid header
    res2 = client.post(
        "/telegram/webhook",
        json={"update_id": 100},
        headers={"X-Telegram-Bot-Api-Secret-Token": "wrong-secret"},
    )
    assert res2.status_code == 401


def test_webhook_dedup_and_dispatch(monkeypatch):
    secret = "valid-secret"
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", secret)
    monkeypatch.setattr(settings, "TELEGRAM_WEBHOOK_SECRET", secret)

    mock_db = MagicMock()
    # First query returns no duplicate
    mock_db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []

    with patch("server.get_supabase_client", return_value=mock_db), patch(
        "server.dispatch_telegram_command"
    ) as mock_dispatch:

        headers = {"X-Telegram-Bot-Api-Secret-Token": secret}
        payload = {"update_id": 999, "message": {"text": "/ready", "chat": {"id": 123}}}

        res = client.post("/telegram/webhook", json=payload, headers=headers)
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}
        mock_dispatch.assert_called_once_with(payload)

    # Test duplicate update_id returns already_processed
    mock_db_dup = MagicMock()
    mock_db_dup.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"update_id": 999}
    ]

    with patch("server.get_supabase_client", return_value=mock_db_dup):
        res_dup = client.post("/telegram/webhook", json=payload, headers=headers)
        assert res_dup.status_code == 200
        assert res_dup.json() == {"status": "already_processed"}


def test_parse_telegram_update():
    up1 = {"message": {"text": "/ready@axis_bot args", "chat": {"id": 111}}}
    cmd, args, chat_id = parse_telegram_update(up1)
    assert cmd == "/ready"
    assert args == "args"
    assert chat_id == "111"

    up2 = {"message": {"text": "/close NIFTY"}}
    cmd2, args2, _ = parse_telegram_update(up2)
    assert cmd2 == "/close"
    assert args2 == "NIFTY"


def test_handle_ready_command():
    mock_db = MagicMock()
    with patch("src.commands.router.send_telegram_alert") as mock_alert:
        handle_ready_command("123", db=mock_db)

        mock_db.table.assert_called_with("trader_session_state")
        mock_db.table().upsert.assert_called_once()
        upsert_arg = mock_db.table().upsert.call_args[0][0]
        assert upsert_arg["is_ready"] is True
        assert "session_date" in upsert_arg
        mock_alert.assert_called_once()
        assert "READY" in mock_alert.call_args[0][2]


def test_handle_resend_command_with_unsent_signal():
    mock_db = MagicMock()
    mock_signal = {
        "id": "sig-123",
        "symbol": "BANKNIFTY",
        "direction_score": 85,
        "active_strategy_slug": "gvof",
        "cycle_timestamp": "2026-08-09T10:00:00Z",
    }
    mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = [
        mock_signal
    ]

    with patch("src.commands.router.send_telegram_alert", return_value=True) as mock_alert:
        handle_resend_command("123", db=mock_db)

        assert mock_alert.call_count == 2  # Resent signal alert + Confirmation alert
        mock_db.table().update.assert_called_with(
            {"telegram_sent": True, "telegram_error": None}
        )


def test_handle_resend_command_no_unsent_signal():
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = []

    with patch("src.commands.router.send_telegram_alert") as mock_alert:
        handle_resend_command("123", db=mock_db)
        mock_alert.assert_called_once()
        assert "No unsent signals" in mock_alert.call_args[0][2]


def test_handle_close_command_with_symbol():
    mock_db = MagicMock()
    with patch("src.commands.router.send_telegram_alert") as mock_alert:
        handle_close_command("nifty", "123", db=mock_db)

        mock_db.table.assert_called_with("active_position")
        mock_db.table().delete.return_value.eq.assert_called_with("symbol", "NIFTY")
        mock_alert.assert_called_once()
        assert "Position closed for NIFTY" in mock_alert.call_args[0][2]


def test_handle_close_command_without_symbol():
    mock_db = MagicMock()
    with patch("src.commands.router.send_telegram_alert") as mock_alert:
        handle_close_command("", "123", db=mock_db)

        mock_db.table.assert_called_with("active_position")
        mock_db.table().delete.return_value.neq.assert_called_with("symbol", "")
        mock_alert.assert_called_once()
        assert "All active positions closed" in mock_alert.call_args[0][2]


def test_handle_record_stub():
    with patch("src.commands.router.send_telegram_alert") as mock_alert:
        handle_record_stub("123")
        mock_alert.assert_called_once()
        assert "not yet implemented" in mock_alert.call_args[0][2]


def test_eod_active_position_cleanup_in_no_trade_summary():
    mock_db = MagicMock()
    mock_db.table.return_value.select.return_value.gte.return_value.execute.return_value.data = []
    mock_db.table.return_value.select.return_value.lt.return_value.execute.return_value.data = []

    with patch("src.scheduling.no_trade_summary.get_supabase_client", return_value=mock_db), patch(
        "src.scheduling.no_trade_summary.send_telegram_alert"
    ):
        run_no_trade_summary()

        # Verify active_position delete call
        mock_db.table.assert_any_call("active_position")
        mock_db.table().delete.return_value.lt.assert_called_once()
