"""Track A Telegram queue/rate limiter tests."""

from __future__ import annotations


class FakeResponse:
    def raise_for_status(self):
        return None


def test_three_alert_burst_is_sent_through_rate_limited_queue(monkeypatch):
    from src.delivery import telegram_formatter

    posts = []
    sleeps = []
    clock = {"value": 100.0}

    def fake_monotonic():
        return clock["value"]

    def fake_sleep(seconds):
        sleeps.append(seconds)
        clock["value"] += seconds

    def fake_post(url, *, json, timeout):
        posts.append({"url": url, "json": dict(json), "timeout": timeout, "at": clock["value"]})
        return FakeResponse()

    telegram_formatter.reset_telegram_queue_for_tests()
    monkeypatch.setattr(telegram_formatter.time, "monotonic", fake_monotonic)
    monkeypatch.setattr(telegram_formatter.time, "sleep", fake_sleep)
    monkeypatch.setattr(telegram_formatter.requests, "post", fake_post)
    monkeypatch.setattr(telegram_formatter, "TELEGRAM_SEND_INTERVAL_SECONDS", 1.0)

    assert telegram_formatter.send_telegram_alert("token", "chat", "first") is True
    assert telegram_formatter.send_telegram_alert("token", "chat", "second") is True
    assert telegram_formatter.send_telegram_alert("token", "chat", "third") is True

    assert len(posts) == 3
    assert len(sleeps) == 2
    assert all(wait >= 1.0 for wait in sleeps)
    assert [post["json"]["text"] for post in posts] == ["first", "second", "third"]
    assert all(post["json"].get("parse_mode") == "MarkdownV2" for post in posts)


def test_interactive_ui_routes_through_shared_queue_and_sanitizer(monkeypatch):
    from src.delivery import interactive_ui

    payloads = []
    monkeypatch.setattr(interactive_ui.settings, "TELEGRAM_BOT_TOKEN", "token", raising=False)
    monkeypatch.setattr(interactive_ui.settings, "TELEGRAM_CHAT_ID", "chat", raising=False)
    monkeypatch.setattr(
        interactive_ui,
        "send_telegram_payload",
        lambda _token, method, payload, timeout=10.0: payloads.append((method, payload)) or True,
    )

    assert interactive_ui.send_cooling_off_ui("2026-07-14T10:30:00+05:30") is True
    method, payload = payloads[-1]
    assert method == "sendMessage"
    assert payload["parse_mode"] == "MarkdownV2"
    assert r"Cooling\-Off Period Until" in payload["text"]
    assert payload["reply_markup"]["inline_keyboard"]
