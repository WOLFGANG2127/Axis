"""Track A live-safety guardrail regression tests.

These tests deliberately exercise the closest safe equivalent of the live
guardrail events: LLM spend accounting and API circuit-breaker trip behavior.
"""

from __future__ import annotations

import asyncio
import sys
import types
from types import SimpleNamespace


class FakeExecute:
    def __init__(self, data=None):
        self.data = data

    def execute(self):
        return SimpleNamespace(data=self.data)


class FakeCostTable:
    def __init__(self, db):
        self.db = db

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def execute(self):
        return SimpleNamespace(data=[self.db.cost_row])


class FakeCostDb:
    def __init__(self, *, spend=0.0, cap=2.0, rpc_totals=None):
        self.cost_row = {"cumulative_spend_usd": spend, "hard_cap_usd": cap}
        self.rpc_totals = list(rpc_totals or [])
        self.rpc_calls = []

    def table(self, name):
        assert name == "llm_cost_guardrail"
        return FakeCostTable(self)

    def rpc(self, name, payload):
        self.rpc_calls.append((name, payload))
        total = self.rpc_totals.pop(0) if self.rpc_totals else payload["p_cost_usd"]
        return FakeExecute(total)


class FakeCircuitTable:
    def __init__(self, db, name):
        self.db = db
        self.name = name
        self.payloads = []

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, *_args, **_kwargs):
        return self

    def upsert(self, payload):
        self.db.upserts.append((self.name, payload))
        return self

    def execute(self):
        return SimpleNamespace(data=self.db.table_rows.get(self.name, []))


class FakeCircuitDb:
    def __init__(self, rpc_counts):
        self.rpc_counts = list(rpc_counts)
        self.rpc_calls = []
        self.upserts = []
        self.table_rows = {"api_circuit_breakers": []}

    def table(self, name):
        return FakeCircuitTable(self, name)

    def rpc(self, name, payload):
        self.rpc_calls.append((name, payload))
        return FakeExecute(self.rpc_counts.pop(0))


def install_fake_litellm(monkeypatch, *, costs, calls):
    async def fake_acompletion(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"decision":"PROCEED"}'))]
        )

    def fake_completion_cost(completion_response):
        return costs.pop(0)

    fake_module = types.SimpleNamespace(
        acompletion=fake_acompletion,
        completion_cost=fake_completion_cost,
    )
    monkeypatch.setitem(sys.modules, "litellm", fake_module)


def test_llm_spend_increment_runs_once_per_actual_llm_call(monkeypatch):
    from src.database import supabase
    from src.config.settings import settings
    from src.llm import router

    db = FakeCostDb(spend=0.0, cap=2.0, rpc_totals=[0.25, 0.50])
    llm_calls = []
    install_fake_litellm(monkeypatch, costs=[0.25, 0.25], calls=llm_calls)
    monkeypatch.setattr(supabase, "get_supabase_client", lambda: db)
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "token", raising=False)
    monkeypatch.setattr(settings, "TELEGRAM_CHAT_ID", "chat", raising=False)

    asyncio.run(router._acompletion("fake/model", "key", [{"role": "user", "content": "one"}]))
    asyncio.run(router._acompletion("fake/model", "key", [{"role": "user", "content": "two"}]))

    assert len(llm_calls) == 2
    assert [name for name, _payload in db.rpc_calls] == [
        "increment_llm_spend",
        "increment_llm_spend",
    ]
    assert [payload["p_cost_usd"] for _name, payload in db.rpc_calls] == [0.25, 0.25]


def test_llm_budget_guardrail_blocks_before_provider_call_and_alerts(monkeypatch):
    from src.database import supabase
    from src.config.settings import settings
    from src.llm import router

    db = FakeCostDb(spend=2.0, cap=2.0)
    llm_calls = []
    alerts = []
    install_fake_litellm(monkeypatch, costs=[0.25], calls=llm_calls)
    monkeypatch.setattr(supabase, "get_supabase_client", lambda: db)
    monkeypatch.setattr(settings, "TELEGRAM_BOT_TOKEN", "token", raising=False)
    monkeypatch.setattr(settings, "TELEGRAM_CHAT_ID", "chat", raising=False)
    monkeypatch.setattr(
        "src.delivery.telegram_formatter.send_telegram_alert",
        lambda _token, _chat, msg: alerts.append(msg) or True,
    )

    try:
        asyncio.run(router._acompletion("fake/model", "key", [{"role": "user", "content": "x"}]))
    except router.BudgetExhaustedError as exc:
        assert "Daily LLM budget" in str(exc)
    else:
        raise AssertionError("budget guardrail did not raise")

    assert llm_calls == []
    assert db.rpc_calls == []
    assert alerts and "Daily LLM budget" in alerts[-1]


def test_circuit_breaker_trips_on_third_consecutive_failure(monkeypatch):
    from src.data import dhan_client
    from src.database import supabase

    db = FakeCircuitDb(rpc_counts=[1, 2, 3])
    alerts = []
    monkeypatch.setattr(supabase, "get_supabase_client", lambda: db)
    monkeypatch.setattr(
        dhan_client,
        "_fire_circuit_alert",
        lambda endpoint, count: alerts.append((endpoint, count)),
    )

    dhan_client._record_failure("optionchain")
    dhan_client._record_failure("optionchain")
    dhan_client._record_failure("optionchain")

    assert [name for name, _payload in db.rpc_calls] == [
        "increment_circuit_failure",
        "increment_circuit_failure",
        "increment_circuit_failure",
    ]
    assert alerts == [("optionchain", 3)]


def test_circuit_breaker_open_recent_failure_returns_safe_default(monkeypatch):
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from src.data import dhan_client
    from src.database import supabase

    db = FakeCircuitDb(rpc_counts=[])
    db.table_rows["api_circuit_breakers"] = [
        {
            "status": "OPEN",
            "last_failure_at": datetime.now(ZoneInfo("UTC")).isoformat(),
        }
    ]
    monkeypatch.setattr(supabase, "get_supabase_client", lambda: db)

    assert dhan_client._can_proceed("optionchain") is False


