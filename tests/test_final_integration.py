"""Final STEP 8-11 integration tests."""

from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

IST = ZoneInfo("Asia/Kolkata")


def _fake_env(monkeypatch):
    values = {
        "GOOGLE_API_KEY": "google",
        "GROQ_API_KEY": "groq",
        "ZAI_API_KEY": "zai",
        "TELEGRAM_BOT_TOKEN": "token",
        "TELEGRAM_CHAT_ID": "123",
        "TELEGRAM_WEBHOOK_SECRET": "webhook-secret",
        "DHAN_CLIENT_ID": "dhan",
        "DHAN_ACCESS_TOKEN": "dhan-token",
        "DHAN_TOTP_SECRET": "totp",
        "DHAN_PIN": "1234",
        "SUPABASE_URL": "https://example.supabase.co",
        "SUPABASE_ANON_KEY": "anon",
        "SUPABASE_SERVICE_ROLE_KEY": "service",
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    sys.modules.pop("src.config.settings", None)


def test_json_extractor_handles_fences_and_trailing_commas():
    from src.llm.json_extractor import extract_json

    raw = """```json
    {"decision":"PROCEED","reasons":["ok",],}
    ```"""
    assert extract_json(raw) == {"decision": "PROCEED", "reasons": ["ok"]}


def test_markdown_v2_escapes_every_special_character():
    from src.delivery.telegram_formatter import MARKDOWN_V2_SPECIALS, sanitize_telegram_md

    escaped = sanitize_telegram_md(MARKDOWN_V2_SPECIALS)
    for char in MARKDOWN_V2_SPECIALS:
        assert f"\\{char}" in escaped


def test_send_telegram_alert_returns_false_on_api_failure(monkeypatch):
    from src.delivery.telegram_formatter import send_telegram_alert

    def fail(*_args, **_kwargs):
        raise RuntimeError("network down")

    monkeypatch.setattr("src.delivery.telegram_formatter.requests.post", fail)
    assert send_telegram_alert("token", "chat", "hello") is False


def test_calendar_gate_uses_ist_hours_and_holidays():
    from src.scheduling.calendar_gate import is_market_open

    assert is_market_open(datetime(2026, 7, 8, 10, 0, tzinfo=IST))
    assert not is_market_open(datetime(2026, 7, 11, 10, 0, tzinfo=IST))
    assert not is_market_open(
        datetime(2026, 7, 8, 10, 0, tzinfo=IST),
        holidays=["2026-07-08"],
    )


def test_correlation_id_is_uuid_shaped():
    from src.observability.correlation import new_correlation_id

    value = new_correlation_id()
    assert len(value) == 36
    assert value.count("-") == 4


def test_lock_manager_local_fallback_acquire_and_release(monkeypatch):
    from src.scheduling import lock_manager

    monkeypatch.setattr(lock_manager, "get_lock_db", lambda: None)
    assert lock_manager.acquire_run_lock("NIFTY") is True
    assert lock_manager.acquire_run_lock("NIFTY") is False
    lock_manager.release_run_lock("NIFTY")
    assert lock_manager.acquire_run_lock("NIFTY") is True
    lock_manager.release_run_lock("NIFTY")


def test_alert_builder_returns_markdown_safe_message():
    from src.delivery.alert_builder import build_alert
    from src.graph.state import AxisState

    message = build_alert(
        AxisState(
            symbol="NIFTY",
            cycle_timestamp=datetime(2026, 7, 8, 10, 0, tzinfo=IST),
            correlation_id="abc",
            direction_score=1,
            structure_confirmed=True,
            active_strategy={"strategy_name": "GVOF", "entry": 24000.0},
            verifier_verdict={"decision": "PROCEED"},
            risk_approved=True,
            dedup_status="CLEAR",
        )
    )
    assert "AXIS SIGNAL" in message
    assert "24000\\.00" in message


def test_router_uses_gemini_then_zai_fallback_and_groq(monkeypatch):
    _fake_env(monkeypatch)
    from src.graph.state import AxisState
    from src.llm import router

    calls = []

    async def fake_acompletion(model, api_key, messages):
        del messages
        calls.append((model, api_key))
        if model == router.ANALYST_PRIMARY_MODEL:
            raise RuntimeError("primary down")
        if model == router.ANALYST_FALLBACK_MODEL:
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content='{"view":"bearish","confidence":0.7}')
                    )
                ]
            )
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content='{"decision":"PROCEED","reason":"ok"}')
                )
            ]
        )

    monkeypatch.setattr(router, "_acompletion", fake_acompletion)
    monkeypatch.setattr(router, 'acquire', lambda *args, **kwargs: asyncio.sleep(0, result=True))
    monkeypatch.setattr(router, 'release', lambda *args, **kwargs: asyncio.sleep(0))
    state = AxisState(symbol="NIFTY", active_strategy={"strategy_name": "GVOF"})
    analyst = asyncio.run(router.call_llm_router("analyst", state))
    verifier = asyncio.run(router.call_llm_router("verifier", state))

    assert analyst["provider"] == "zai"
    assert analyst["fallback_from"] == "gemini"
    assert verifier["provider"] == "groq"
    assert verifier["decision"] == "PROCEED"
    assert calls == [
        (router.ANALYST_PRIMARY_MODEL, "google"),
        (router.ANALYST_FALLBACK_MODEL, "zai"),
        (router.VERIFIER_MODEL, "groq"),
    ]


def test_run_cycle_releases_lock_in_finally(monkeypatch):
    import main

    events = []

    class FakeGraph:
        async def ainvoke(self, state):
            events.append(("graph", state["symbol"]))
            return {"symbol": state["symbol"], "correlation_id": state["correlation_id"]}

    monkeypatch.setattr(main, "is_market_open", lambda _now: True)
    monkeypatch.setattr(main, "is_system_paused", lambda db=None: (False, None))
    monkeypatch.setattr(main, 'check_prs_trading_gate', lambda **kwargs: type('Gate', (), {'allowed': True})())
    monkeypatch.setattr(main, "acquire_run_lock", lambda symbol, db=None, now=None: events.append(("acquire", symbol)) or True)
    monkeypatch.setattr(main, "release_run_lock", lambda symbol, db=None: events.append(("release", symbol)))

    result = asyncio.run(
        main.run_cycle(
            "NIFTY",
            now=datetime(2026, 7, 8, 10, 0, tzinfo=IST),
            graph=FakeGraph(),
        )
    )
    assert result["status"] == "COMPLETED"
    assert events == [("acquire", "NIFTY"), ("graph", "NIFTY"), ("release", "NIFTY")]


def test_main_rejects_invalid_symbol():
    import main

    with pytest.raises(ValueError):
        asyncio.run(main.run_cycle("FINNIFTY", now=datetime(2026, 7, 8, 10, 0, tzinfo=IST)))

