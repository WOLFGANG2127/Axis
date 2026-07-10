"""Build the final seven-section AXIS Telegram alert."""

from __future__ import annotations

from typing import Any, Mapping

from src.delivery.telegram_formatter import sanitize_telegram_md
from src.graph.state import AxisState


def _fmt(value: Any, default: str = "NA") -> str:
    if value is None:
        return default
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def _strategy_value(strategy: Mapping[str, Any], key: str) -> str:
    return _fmt(strategy.get(key))


def build_alert(state: AxisState) -> str:
    """Assemble a Telegram-safe, MarkdownV2-escaped alert body."""

    strategy = state.active_strategy or {}
    context = state.market_context or {}
    verifier = state.verifier_verdict or {}
    decision = verifier.get("decision") if isinstance(verifier, Mapping) else verifier

    # Drawdown Recovery Text (Prompt 25)
    dd_pct = context.get("portfolio_drawdown_pct") or strategy.get("drawdown_pct") or 0.0
    dd_text = ""
    try:
        if float(dd_pct) > 10.0:
            dd = float(dd_pct) / 100.0 if float(dd_pct) > 1.0 else float(dd_pct)
            if dd < 1.0:
                recovery = (1 / (1 - dd)) - 1
                dd_text = f"\n⚠️ Drawdown at {dd*100:.1f}% | Requires {recovery*100:.1f}% gain to recover"
    except Exception:
        pass
        
    # Half-Kelly Transparency (Prompt 28)
    win_rate = strategy.get("win_rate")
    payoff = strategy.get("r_multiple_avg") or strategy.get("avg_gain")
    lots = strategy.get("lots")
    if lots is None:
        size_text = "NA"
    elif win_rate and payoff:
        size_text = f"{lots} Lots (Half-Kelly calculated via {float(win_rate)*100:.1f}% Win Rate & {float(payoff):.2f} Payoff)"
    else:
        size_text = f"{lots} Lots"

    raw = "\n".join(
        [
            "AXIS SIGNAL",
            "",
            "1. Session Context",
            f"Symbol: {_fmt(state.symbol)}",
            f"Cycle: {_fmt(state.cycle_timestamp)}",
            f"Correlation: {_fmt(state.correlation_id)}",
            "",
            "2. Signal Conditions",
            f"Direction Score: {_fmt(state.direction_score)}",
            f"Structure Confirmed: {_fmt(state.structure_confirmed)}",
            f"Strategy: {_strategy_value(strategy, 'strategy_name')}",
            f"Mode: {_strategy_value(strategy, 'mode')}",
            "",
            "3. Order Flow",
            f"GEX: {_strategy_value(strategy, 'gex')}",
            f"IB High: {_strategy_value(strategy, 'ib_high')}",
            f"IB Low: {_strategy_value(strategy, 'ib_low')}",
            f"VIX: {_fmt(context.get('vix'))}",
            "",
            "4. EV / Risk",
            f"Risk Approved: {_fmt(state.risk_approved)}{dd_text}",
            f"Stop Distance: {_strategy_value(strategy, 'stop_distance')}",
            f"No Averaging Losers: {_strategy_value(strategy, 'never_average_loser')}",
            "",
            "5. Options Intelligence",
            f"Target 2 VIX Move: {_strategy_value(strategy, 'target_2')}",
            f"Data Quality: {_fmt(state.data_quality)}",
            "",
            "6. Trade Parameters",
            f"Size: {size_text}",
            f"Entry: {_strategy_value(strategy, 'entry')}",
            f"Stop Loss: {_strategy_value(strategy, 'stop_loss')}",
            f"Target 1: {_strategy_value(strategy, 'target_1')}",
            f"T1 Exit: {_strategy_value(strategy, 'target_1_exit_pct')}%",
            "",
            "7. Verdict",
            f"Verifier: {_fmt(decision)}",
            f"Dedup: {_fmt(state.dedup_status)}",
            "",
            "[PYRAMID DIRECTIVE: Pending Tier 5 Implementation]"
        ]
    )
    return sanitize_telegram_md(raw)
