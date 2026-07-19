"""Track A PRS fail-closed trading gate tests."""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")


class FakeTable:
    def __init__(self, db, name: str):
        self.db = db
        self.name = name
        self.filters = []

    def select(self, *_args, **_kwargs):
        return self

    def eq(self, key, value):
        self.filters.append((key, value))
        return self

    def execute(self):
        rows = list(self.db.rows.get(self.name, []))
        for key, value in self.filters:
            rows = [row for row in rows if row.get(key) == value]
        return SimpleNamespace(data=[dict(row) for row in rows])


class FakeDb:
    def __init__(self, rows=None):
        self.rows = rows or {"trader_session_state": []}

    def table(self, name: str):
        return FakeTable(self, name)


def _now(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 7, 14, hour, minute, tzinfo=IST)


def test_prs_missing_after_cutoff_blocks_trading():
    from src.scheduling.prs_gate import check_prs_trading_gate

    result = check_prs_trading_gate(db=FakeDb(), now=_now(9, 15))

    assert result.allowed is False
    assert result.reason == "PRS_MISSING_AFTER_CUTOFF"
    assert result.cutoff_ist == "09:10"


def test_prs_answered_late_after_cutoff_blocks_trading():
    from src.scheduling.prs_gate import check_prs_trading_gate

    db = FakeDb({"trader_session_state": [{
        "trading_date": "2026-07-14",
        "prs_completed": True,
        "is_trading_blocked": False,
        "prs_completed_at": "2026-07-14T09:11:00+05:30",
        "prs_score": 8,
    }]})

    result = check_prs_trading_gate(db=db, now=_now(9, 15))

    assert result.allowed is False
    assert result.reason == "PRS_COMPLETED_AFTER_CUTOFF"


def test_prs_completed_on_time_allows_trading():
    from src.scheduling.prs_gate import check_prs_trading_gate

    db = FakeDb({"trader_session_state": [{
        "trading_date": "2026-07-14",
        "prs_completed": True,
        "is_trading_blocked": False,
        "prs_completed_at": "2026-07-14T09:05:00+05:30",
        "prs_score": 8,
    }]})

    result = check_prs_trading_gate(db=db, now=_now(9, 15))

    assert result.allowed is True
    assert result.reason is None


def test_prs_completed_with_blocking_score_blocks_trading():
    from src.scheduling.prs_gate import check_prs_trading_gate

    db = FakeDb({"trader_session_state": [{
        "trading_date": "2026-07-14",
        "prs_completed": True,
        "is_trading_blocked": True,
        "prs_completed_at": "2026-07-14T09:05:00+05:30",
        "prs_score": 4,
    }]})

    result = check_prs_trading_gate(db=db, now=_now(9, 15))

    assert result.allowed is False
    assert result.reason == "PRS_SCORE_BLOCKED"


def test_run_cycle_stops_before_lock_when_prs_blocks(monkeypatch):
    import asyncio
    import main

    events = []
    monkeypatch.setattr(main, "is_market_open", lambda _now: True)
    monkeypatch.setattr(main, "is_system_paused", lambda db=None: (False, None))
    monkeypatch.setattr(main, "acquire_run_lock", lambda *args, **kwargs: events.append("lock") or True)

    result = asyncio.run(main.run_cycle("NIFTY", db=FakeDb(), now=_now(9, 15), graph=object()))

    assert result["status"] == "PRS_BLOCKED"
    assert result["reason"] == "PRS_MISSING_AFTER_CUTOFF"
    assert events == []

def test_prs_late_cron_tick_uses_same_cutoff_decision():
    from src.scheduling.prs_gate import check_prs_trading_gate
    db = FakeDb({"trader_session_state": [{"trading_date": "2026-07-14", "prs_completed": True, "is_trading_blocked": False, "prs_completed_at": "2026-07-14T09:11:00+05:30"}]})
    assert check_prs_trading_gate(db=db, now=_now(9, 10)).reason == "PRS_COMPLETED_AFTER_CUTOFF"
    assert check_prs_trading_gate(db=db, now=_now(9, 13)).reason == "PRS_COMPLETED_AFTER_CUTOFF"


def test_prs_converts_utc_runner_clock_to_ist_before_cutoff():
    from src.scheduling.prs_gate import check_prs_trading_gate
    utc = ZoneInfo("UTC")
    db = FakeDb({"trader_session_state": [{"trading_date": "2026-07-14", "prs_completed": True, "is_trading_blocked": False, "prs_completed_at": "2026-07-14T03:35:00+00:00"}]})
    result = check_prs_trading_gate(db=db, now=datetime(2026, 7, 14, 3, 45, tzinfo=utc))
    assert result.allowed is True
