"""BankNifty Shadow-Mode Gate implementation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from src.database.supabase import get_supabase_client
from src.database.table_routing import get_table_name
from src.config.constants import (
    BANKNIFTY_SHADOW_MIN_SESSIONS,
    BANKNIFTY_SHADOW_MIN_PROFIT_FACTOR,
    BANKNIFTY_SHADOW_MIN_WIN_RATE,
    BANKNIFTY_SHADOW_MAX_DRAWDOWN_PCT,
)
from src.data.event_calendar import get_monthly_expiries

def get_banknifty_shadow_status(virtual_portfolio_id: int, is_backtest: bool = False) -> dict[str, Any]:
    """Evaluate all six conditions for the BankNifty shadow mode gate."""
    client = get_supabase_client()
    
    vp_res = client.table("virtual_portfolios").select("*").eq("id", virtual_portfolio_id).execute()
    if not vp_res.data:
        raise ValueError(f"Virtual portfolio {virtual_portfolio_id} not found")
    vp = vp_res.data[0]
    # SAFETY: NULL or missing fill_realism_audit_passed MUST default to False (BLOCK).
    # Never allow a corrupted or absent value to slip through as truthy.
    raw_fill_realism = vp.get("fill_realism_audit_passed")
    fill_realism_audit_passed = raw_fill_realism is True  # Only explicit True passes
    
    trades_res = client.table(get_table_name("paper_trades", is_backtest)).select("entry_time,exit_time,pnl_rupees").eq("virtual_portfolio_id", virtual_portfolio_id).execute()
    trades = trades_res.data or []
    
    sessions_elapsed = len(set(datetime.fromisoformat(t["entry_time"].replace("Z", "+00:00")).date() for t in trades if t.get("entry_time")))
    sessions_ok = sessions_elapsed >= BANKNIFTY_SHADOW_MIN_SESSIONS
    
    spans_two_expiry_cycles = False
    if trades:
        valid_dates = [datetime.fromisoformat(t["entry_time"].replace("Z", "+00:00")).date() for t in trades if t.get("entry_time")]
        if valid_dates:
            earliest = min(valid_dates)
            latest = max(valid_dates)
            
            expiries = get_monthly_expiries()
            # straddle at least two distinct monthly-expiry boundaries
            expiries_in_range = [e for e in expiries if earliest <= e <= latest]
            spans_two_expiry_cycles = len(set(expiries_in_range)) >= 2

    closed_trades = [t for t in trades if t.get("pnl_rupees") is not None]
    wins = [t for t in closed_trades if float(t["pnl_rupees"]) > 0]
    win_rate = len(wins) / len(closed_trades) if closed_trades else 0.0
    win_rate_ok = win_rate >= BANKNIFTY_SHADOW_MIN_WIN_RATE
    
    gross_profit = sum(float(t["pnl_rupees"]) for t in wins)
    losses = [t for t in closed_trades if float(t["pnl_rupees"]) < 0]
    gross_loss = sum(abs(float(t["pnl_rupees"])) for t in losses)
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else (float('inf') if gross_profit > 0 else 0.0)
    profit_factor_ok = profit_factor >= BANKNIFTY_SHADOW_MIN_PROFIT_FACTOR
    
    max_drawdown_pct = 0.0
    allocated_capital = float(vp.get("capital", 100000.0))
    peak_equity = allocated_capital
    running_equity = allocated_capital
    
    for t in sorted(closed_trades, key=lambda x: x.get("exit_time", "")):
        running_equity += float(t["pnl_rupees"])
        if running_equity > peak_equity:
            peak_equity = running_equity
        
        drawdown_rupees = peak_equity - running_equity
        drawdown_pct = drawdown_rupees / allocated_capital
        if drawdown_pct > max_drawdown_pct:
            max_drawdown_pct = drawdown_pct

    drawdown_ok = max_drawdown_pct <= BANKNIFTY_SHADOW_MAX_DRAWDOWN_PCT

    all_criteria_met = all([
        sessions_ok,
        spans_two_expiry_cycles,
        profit_factor_ok,
        win_rate_ok,
        drawdown_ok,
        fill_realism_audit_passed
    ])

    return {
        "sessions_elapsed": sessions_elapsed,
        "sessions_ok": sessions_ok,
        "spans_two_expiry_cycles": spans_two_expiry_cycles,
        "profit_factor": profit_factor,
        "profit_factor_ok": profit_factor_ok,
        "win_rate": win_rate,
        "win_rate_ok": win_rate_ok,
        "max_drawdown_pct": max_drawdown_pct,
        "drawdown_ok": drawdown_ok,
        "fill_realism_audit_passed": fill_realism_audit_passed,
        "all_criteria_met": all_criteria_met
    }
