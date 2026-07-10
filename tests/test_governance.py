import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import json

from src.risk.risk_manager import validate_asymmetry, check_daily_drawdown
from src.journal.outcome_recorder import record_outcome

IST = ZoneInfo("Asia/Kolkata")

class TestGovernance(unittest.TestCase):
    
    # -------------------------------------------------------------
    # 1. R:R Filter Tests
    # -------------------------------------------------------------
    
    def test_rr_filter_exactly_2_0(self):
        """Test that an R:R of exactly 2.0 passes (Boundary Check)"""
        # Risk = abs(100 - 90) = 10
        # Reward = abs(120 - 100) = 20
        # R:R = 20 / 10 = 2.0 -> Should pass
        self.assertTrue(validate_asymmetry(100.0, 90.0, 120.0))

    def test_rr_filter_sub_2_0(self):
        """Test that a sub-2.0 R:R is blocked"""
        # Risk = abs(100 - 90) = 10
        # Reward = abs(119 - 100) = 19
        # R:R = 19 / 10 = 1.9 -> Should block (return False)
        self.assertFalse(validate_asymmetry(100.0, 90.0, 119.0))
        
    # NOTE: The node-level SHADOW mode logic for R:R wasn't implemented 
    # directly inside validate_asymmetry. If the user expects tests on verifier_node, 
    # they would go here. But validating the strict asymmetry math is primary.

    # -------------------------------------------------------------
    # 2. Daily Loss Breaker Tests
    # -------------------------------------------------------------
    
    @patch('src.risk.risk_manager.settings')
    @patch('src.risk.risk_manager.get_supabase_client')
    def test_daily_loss_breaker_frequency_enforce(self, mock_get_client, mock_settings):
        """Test that the breaker trips strictly on 3 losses in ENFORCE mode"""
        mock_settings.GOVERNANCE_DAILY_LOSS_MODE = "ENFORCE"
        db_mock = MagicMock()
        mock_get_client.return_value = db_mock
        
        # Safe magnitude
        db_mock.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"current_drawdown": 1000.0, "max_loss_limit": 5000.0}
        ]
        
        # Breached frequency (3 losses)
        db_mock.table.return_value.select.return_value.gte.return_value.execute.return_value.data = [
            {"pnl_rupees": -500}, {"pnl_rupees": -600}, {"pnl_rupees": -100}
        ]
        
        self.assertFalse(check_daily_drawdown())
        
    @patch('src.risk.risk_manager.settings')
    @patch('src.risk.risk_manager.get_supabase_client')
    def test_daily_loss_breaker_magnitude_enforce(self, mock_get_client, mock_settings):
        """Test that the breaker trips independently on magnitude in ENFORCE mode"""
        mock_settings.GOVERNANCE_DAILY_LOSS_MODE = "ENFORCE"
        db_mock = MagicMock()
        mock_get_client.return_value = db_mock
        
        # Breached magnitude (e.g., 2.5% drawdown)
        db_mock.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"current_drawdown": 5100.0, "max_loss_limit": 5000.0}
        ]
        
        # Safe frequency (0 losses)
        db_mock.table.return_value.select.return_value.gte.return_value.execute.return_value.data = []
        
        self.assertFalse(check_daily_drawdown())
        
    @patch('src.risk.risk_manager.settings')
    @patch('src.risk.risk_manager.get_supabase_client')
    def test_daily_loss_breaker_shadow_mode(self, mock_get_client, mock_settings):
        """Test that the breaker only logs and passes in SHADOW mode despite being breached"""
        mock_settings.GOVERNANCE_DAILY_LOSS_MODE = "SHADOW"
        db_mock = MagicMock()
        mock_get_client.return_value = db_mock
        
        # Breached on both
        db_mock.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"current_drawdown": 6000.0, "max_loss_limit": 5000.0}
        ]
        db_mock.table.return_value.select.return_value.gte.return_value.execute.return_value.data = [
            {"pnl_rupees": -100}] * 3
            
        # Must pass in SHADOW mode
        self.assertTrue(check_daily_drawdown())

    # -------------------------------------------------------------
    # 3. Behavioral Auto-Tagging Tests
    # -------------------------------------------------------------

    @patch('src.journal.outcome_recorder._database')
    @patch('src.journal.outcome_recorder._update_dynamic_drawdown_limit')
    @patch('src.journal.outcome_recorder.classify_vix_move')
    def test_behavioral_tags_revenge_trade(self, mock_classify, mock_update_limit, mock_db):
        """Test REVENGE_TRADE exact boundary conditions (19 min vs 20.0 min)"""
        mock_classify.return_value = "normal"
        db_mock = MagicMock()
        mock_db.return_value = db_mock
        
        now = datetime.now(IST)
        
        def run_with_diff(diff_minutes):
            entry_time = now
            last_loss_exit = now - timedelta(minutes=diff_minutes)
            
            trade_data = [{
                "id": 1,
                "symbol": "NIFTY",
                "entry_time": entry_time.isoformat(),
                "exit_time": (entry_time + timedelta(minutes=5)).isoformat(),
                "pnl_rupees": 500,
                "pre_trade_checklist": json.dumps({"kelly_recommended_lots": 10}),
                "lots": 10 
            }]
            
            table_mock = db_mock.table.return_value
            table_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = trade_data
            
            # Setup last loss fetch
            table_mock.select.return_value.lt.return_value.lt.return_value.order.return_value.limit.return_value.execute.return_value.data = [
                {"exit_time": last_loss_exit.isoformat()}
            ]
            
            insert_mock = table_mock.insert
            insert_mock.return_value.execute.return_value.data = [{"inserted": True}]
            
            record_outcome(1)
            
            call_args = insert_mock.call_args[0][0]
            return call_args.get("behavioral_outcome_category")
            
        # < 20.0 minutes -> REVENGE_TRADE
        self.assertEqual(run_with_diff(19.99), "REVENGE_TRADE")
        # Exactly 20.0 minutes -> Safe (None)
        self.assertIsNone(run_with_diff(20.0))

    @patch('src.journal.outcome_recorder._database')
    @patch('src.journal.outcome_recorder._update_dynamic_drawdown_limit')
    @patch('src.journal.outcome_recorder.classify_vix_move')
    def test_behavioral_tags_oversize_conviction(self, mock_classify, mock_update_limit, mock_db):
        """Test OVERSIZE_CONVICTION exact boundary conditions (1.26x vs 1.25x Kelly)"""
        mock_classify.return_value = "normal"
        db_mock = MagicMock()
        mock_db.return_value = db_mock
        
        def run_with_size(actual_lots, kelly_lots):
            trade_data = [{
                "id": 1,
                "symbol": "NIFTY",
                "exit_time": datetime.now(IST).isoformat(),
                "pnl_rupees": 500,
                "pre_trade_checklist": json.dumps({"kelly_recommended_lots": kelly_lots}),
                "lots": actual_lots
            }]
            
            table_mock = db_mock.table.return_value
            table_mock.select.return_value.eq.return_value.limit.return_value.execute.return_value.data = trade_data
            
            # No revenge trade match
            table_mock.select.return_value.lt.return_value.lt.return_value.order.return_value.limit.return_value.execute.return_value.data = []
            
            insert_mock = table_mock.insert
            insert_mock.return_value.execute.return_value.data = [{"inserted": True}]
            
            record_outcome(1)
            
            call_args = insert_mock.call_args[0][0]
            return call_args.get("behavioral_outcome_category")
            
        # > 1.25x -> OVERSIZE_CONVICTION
        # 10 Kelly * 1.26 = 12.6. Actual 12.6 is > 1.25x (1.26x)
        self.assertEqual(run_with_size(12.6, 10), "OVERSIZE_CONVICTION")
        # Exactly 1.25x -> Safe (None). 10 * 1.25 = 12.5
        self.assertIsNone(run_with_size(12.5, 10))
        # 1.24x -> Safe (None). 10 * 1.24 = 12.4
        self.assertIsNone(run_with_size(12.4, 10))

if __name__ == '__main__':
    unittest.main()
