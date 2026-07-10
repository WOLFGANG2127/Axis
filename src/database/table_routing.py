"""Dynamic table routing for isolating live vs. backtest data."""

from __future__ import annotations

# Exhaustive allowlist: only these tables may ever be routed to _backtest copies.
# Any table NOT in this set is a live-only system table (accuracy_log,
# scoring_config, virtual_portfolios, broker_tokens, etc.) and MUST NEVER
# receive a _backtest suffix — doing so would silently create an empty shadow
# table that returns zero rows, corrupting sizing and reweighting logic.
_BACKTEST_ROUTABLE = frozenset({
    "paper_trades",
    "signals",
    "market_context_snapshots",
})


def get_table_name(base_name: str, is_backtest: bool) -> str:
    """Return the _backtest suffixed table name if running in a backtest context.

    Raises ValueError if called with a table not in the allowlist, preventing
    accidental creation of shadow tables that don't exist in the schema.
    """
    if not is_backtest:
        return base_name
    if base_name not in _BACKTEST_ROUTABLE:
        raise ValueError(
            f"table_routing: '{base_name}' is not in the backtest-routable "
            f"allowlist {sorted(_BACKTEST_ROUTABLE)}. This is a safety guard — "
            f"routing a live-only table to a _backtest copy would return empty "
            f"data and silently corrupt downstream logic."
        )
    return f"{base_name}_backtest"
