import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, date, timezone
from src.journal.shadow_mode_gate import get_banknifty_shadow_status

class TestBankNiftyShadowGate(unittest.TestCase):
    @patch("src.journal.shadow_mode_gate.get_supabase_client")
    @patch("src.journal.shadow_mode_gate.get_monthly_expiries")
    def test_shadow_mode_criteria(self, mock_expiries, mock_supabase):
        # 1. Setup mock expiries
        mock_expiries.return_value = {date(2026, 1, 29), date(2026, 2, 26), date(2026, 3, 26)}

        # 2. Base perfect case
        # To get sessions_elapsed >= 45, we can just generate 45 distinct dates
        base_trades = []
        for i in range(1, 46):
            # i ranges from 1 to 45. We can just use day = (i%28)+1.
            month = 1 if i <= 15 else (2 if i <= 30 else 3)
            day = (i % 28) + 1
            trade_date = date(2026, month, day)
            pnl = 200.0 if i <= 27 else -100.0
            dt_iso = datetime(trade_date.year, trade_date.month, trade_date.day, tzinfo=timezone.utc).isoformat()
            base_trades.append({"entry_time": dt_iso, "exit_time": dt_iso, "pnl_rupees": pnl})

        def run_test_case(fill_realism, override_trades=None):
            mock_client = MagicMock()
            mock_supabase.return_value = mock_client
            
            mock_vp_res = MagicMock()
            mock_vp_res.data = [{"id": 1, "symbol": "BANKNIFTY", "capital": 100000.0, "fill_realism_audit_passed": fill_realism}]
            mock_client.table().select().eq().execute.side_effect = [mock_vp_res, MagicMock(data=override_trades or base_trades)]
            
            return get_banknifty_shadow_status(1)

        # A. Perfect, but fill_realism = False
        res_a = run_test_case(False)
        self.assertTrue(res_a["sessions_ok"])
        self.assertTrue(res_a["spans_two_expiry_cycles"])
        self.assertTrue(res_a["profit_factor_ok"])
        self.assertTrue(res_a["win_rate_ok"])
        self.assertTrue(res_a["drawdown_ok"])
        self.assertFalse(res_a["fill_realism_audit_passed"])
        self.assertFalse(res_a["all_criteria_met"])

        # B. Perfect, fill_realism = True -> Should pass completely
        res_b = run_test_case(True)
        self.assertTrue(res_b["all_criteria_met"])

        # C. Test each condition failing individually (with realism=True)
        # Fail sessions (<45)
        res_fail_sessions = run_test_case(True, override_trades=base_trades[:40])
        self.assertFalse(res_fail_sessions["sessions_ok"])
        self.assertFalse(res_fail_sessions["all_criteria_met"])

        # Fail expiry cycles (only spans one)
        # We can just change mock_expiries to only have 1 expiry so it's impossible to span 2
        mock_expiries.return_value = {date(2026, 2, 26)}
        bad_expiry_trades = base_trades  # base_trades has 45 distinct dates
        res_fail_expiry = run_test_case(True, override_trades=bad_expiry_trades)
        self.assertTrue(res_fail_expiry["sessions_ok"])
        self.assertFalse(res_fail_expiry["spans_two_expiry_cycles"])
        self.assertFalse(res_fail_expiry["all_criteria_met"])
        # Restore mock_expiries for the rest
        mock_expiries.return_value = {date(2026, 1, 29), date(2026, 2, 26), date(2026, 3, 26)}

        # Fail win rate (<0.55)
        # 45 trades, 20 wins, 25 losses (win rate 44%)
        # Profit factor still > 1.5 if wins are 300, losses are 100. PF = 6000/2500 = 2.4
        fail_wr_trades = []
        for i in range(1, 46):
            month = 1 if i <= 15 else (2 if i <= 30 else 3)
            day = (i % 28) + 1
            dt_iso = datetime(2026, month, day, tzinfo=timezone.utc).isoformat()
            pnl = 300.0 if i <= 20 else -100.0
            fail_wr_trades.append({"entry_time": dt_iso, "exit_time": dt_iso, "pnl_rupees": pnl})
        res_fail_wr = run_test_case(True, override_trades=fail_wr_trades)
        self.assertTrue(res_fail_wr["profit_factor_ok"])
        self.assertFalse(res_fail_wr["win_rate_ok"])
        self.assertFalse(res_fail_wr["all_criteria_met"])

        # Fail profit factor (<1.5)
        # 45 trades, 27 wins (60%), 18 losses
        # Profit factor 1.0 (wins = 100, losses = 150 -> 2700 / 2700 = 1.0)
        fail_pf_trades = []
        for i in range(1, 46):
            month = 1 if i <= 15 else (2 if i <= 30 else 3)
            day = (i % 28) + 1
            dt_iso = datetime(2026, month, day, tzinfo=timezone.utc).isoformat()
            pnl = 100.0 if i <= 27 else -150.0
            fail_pf_trades.append({"entry_time": dt_iso, "exit_time": dt_iso, "pnl_rupees": pnl})
        res_fail_pf = run_test_case(True, override_trades=fail_pf_trades)
        self.assertTrue(res_fail_pf["win_rate_ok"])
        self.assertFalse(res_fail_pf["profit_factor_ok"])
        self.assertFalse(res_fail_pf["all_criteria_met"])

        # Fail max drawdown (>2%)
        # Drawdown > 2% of 100k is > 2000 rupees.
        # We start with 1 loss of -3000, then all wins to recover win rate/PF.
        fail_dd_trades = []
        for i in range(1, 46):
            month = 1 if i <= 15 else (2 if i <= 30 else 3)
            day = (i % 28) + 1
            dt_iso = datetime(2026, month, day, tzinfo=timezone.utc).isoformat()
            pnl = 200.0 if i > 15 else -300.0  # 15 losses of 300 = 4500 drawdown
            fail_dd_trades.append({"entry_time": dt_iso, "exit_time": dt_iso, "pnl_rupees": pnl})
        res_fail_dd = run_test_case(True, override_trades=fail_dd_trades)
        self.assertFalse(res_fail_dd["drawdown_ok"])
        self.assertFalse(res_fail_dd["all_criteria_met"])
        
        print("[PASS] All BankNifty Shadow Mode conditions verified explicitly.")

if __name__ == "__main__":
    unittest.main()
