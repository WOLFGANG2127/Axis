"""Dynamic table routing for isolating live vs. backtest data."""

from __future__ import annotations

def get_table_name(base_name: str, is_backtest: bool) -> str:
    """Return the _backtest suffixed table name if running in a backtest context."""
    return f"{base_name}_backtest" if is_backtest else base_name
