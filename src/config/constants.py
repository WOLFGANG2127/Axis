"""Shared numeric and market constants."""

from __future__ import annotations

LOT_SIZE_NIFTY = 65
LOT_SIZE_BANKNIFTY = 30
LOT_SIZE_NIFTYNXT50 = 25

BANKNIFTY_SHADOW_MIN_SESSIONS = 45
BANKNIFTY_SHADOW_MIN_PROFIT_FACTOR = 1.5
BANKNIFTY_SHADOW_MIN_WIN_RATE = 0.55
BANKNIFTY_SHADOW_MAX_DRAWDOWN_PCT = 0.02

def get_lot_size(symbol: str) -> int:
    symbol = symbol.strip().upper()
    if symbol == "NIFTY":
        return LOT_SIZE_NIFTY
    elif symbol == "BANKNIFTY":
        return LOT_SIZE_BANKNIFTY
    elif symbol == "NIFTYNXT50":
        return LOT_SIZE_NIFTYNXT50
    raise ValueError(f"Unknown symbol: {symbol}")

RISK_FLAT_PCT = 0.01
KELLY_CAP_PCT = 0.02
KELLY_MIN_SAMPLE = 30
ACCURACY_MIN_SAMPLE = 15

GVOF_IB_MIN_RANGE = 50
GVOF_IB_END = (10, 35)
GVOF_ENTRY_BUFFER = 2
GVOF_STOP_BUFFER = 5
GVOF_STOP_IB_PCT = 0.06
GVOF_T1_OFFSET = 15
GVOF_HARD_EXIT = (14, 30)
GVOF_NO_ENTRY_AFTER = (14, 0)

MARKET_OPEN = (9, 15)
MARKET_CLOSE = (15, 30)

DEFAULT_RISK_FREE_RATE = 0.065
