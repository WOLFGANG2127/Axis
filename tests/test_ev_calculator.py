"""Tests for expected value calculations and lot size correctness."""

import pytest
from src.config.constants import get_lot_size
from src.math.pricing import expected_value, transaction_cost

def test_lot_size_lookup_correctness():
    assert get_lot_size("NIFTY") == 65
    assert get_lot_size("BANKNIFTY") == 30

def test_ev_calculation_with_corrected_nifty_lot_size():
    lot_size = get_lot_size("NIFTY") # 65
    entry_price = 100.0
    stop_loss = 90.0
    target_price = 120.0
    
    # 65 lot size: loss is 10 points -> 650 rs risk per lot
    # Gain is 20 points -> 1300 rs gain per lot
    win_prob = 0.6
    
    # Example premium to calculate transaction cost
    premium = entry_price * lot_size
    cost = transaction_cost(premium)
    
    ev = expected_value(win_prob, 1300.0, 650.0, cost)
    # 0.6 * 1300 - 0.4 * 650 - cost = 780 - 260 - cost = 520 - cost
    assert ev == pytest.approx(520.0 - cost, abs=1e-2)

def test_ev_calculation_with_corrected_banknifty_lot_size():
    lot_size = get_lot_size("BANKNIFTY") # 30
    entry_price = 100.0
    
    premium = entry_price * lot_size
    cost = transaction_cost(premium)
    
    # Win prob 0.5, Gain 1000, Loss 500
    ev = expected_value(0.5, 1000.0, 500.0, cost)
    # 0.5 * 1000 - 0.5 * 500 - cost = 500 - 250 - cost = 250 - cost
    assert ev == pytest.approx(250.0 - cost, abs=1e-2)
