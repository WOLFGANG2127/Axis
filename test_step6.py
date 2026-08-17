import unittest
import numpy as np
from unittest.mock import patch, MagicMock
from src.journal.accuracy_engine import run_lasso_reweighting

class TestLassoReweighting(unittest.TestCase):
    @patch("sklearn.linear_model.LassoCV")
    @patch("src.journal.accuracy_engine._database")
    def test_lasso_floor_logic(self, mock_db, mock_lasso_class):
        mock_client = MagicMock()
        mock_db.return_value = mock_client
        
        # 1. Setup mock synthetic trades (55 trades)
        trades = []
        signals = []
        snapshots = []
        for i in range(1, 56):
            trades.append({"id": i, "signal_id": i, "status": "CLOSED", "r_multiple_achieved": 2.0})
            signals.append({"id": i, "market_snapshot_id": i})
            snapshots.append({
                "id": i,
                "symbol": "NIFTY" if i % 2 == 0 else "BANKNIFTY",
                "gex_value": 0.5,
                "vix_level": 14.0,
                "fii_futures_long_pct": 0.6,
                "order_flow_score": 0.8,
                "pcr_value": 1.1,
                "pcr_divergence": 0.05
            })
            
        mock_client.table().select().eq().execute.return_value.data = trades
        mock_client.table().select().in_().execute.side_effect = [
            MagicMock(data=signals),
            MagicMock(data=snapshots)
        ]
        
        # 2. Mock LassoCV to return some zero coefficients to test the floor logic
        mock_model_instance = MagicMock()
        # Coefs: w_gex, w_vix, w_fii, w_order_flow, w_pcr, w_pcr_divergence
        # VIX and PCR Divergence zeroed out by Lasso
        mock_model_instance.coef_ = np.array([0.5, 0.0, 0.3, 0.8, -0.2, 0.0])
        mock_lasso_class.return_value = mock_model_instance
        
        # 3. Run function
        result = run_lasso_reweighting(min_sample_count=50)
        
        # 4. Verify floor logic
        # Negative coeff (-0.2) becomes 0.10
        # Zero coeff (0.0) becomes 0.10
        # 0.3 remains 0.3
        # 0.5 remains 0.5
        # 0.8 remains 0.8
        
        # raw_layer_a = 0.5 (gex) + 0.10 (vix) + 0.10 (pcr) + 0.0 (pcr_div * validation_flag=0) = 0.70
        # raw_layer_b = 0.30 (fii)
        # raw_layer_c = 0.80 (order_flow)
        # total = 1.80
        
        # layer_a_weight = 0.70 / 1.80 = 0.3888...
        # layer_b_weight = 0.30 / 1.80 = 0.1666...
        # layer_c_weight = 0.80 / 1.80 = 0.4444...
        
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["layer_a_weight"], 0.70 / 1.80, places=4)
        self.assertAlmostEqual(result["layer_b_weight"], 0.30 / 1.80, places=4)
        self.assertAlmostEqual(result["layer_c_weight"], 0.80 / 1.80, places=4)
        
        print("[PASS] Lasso floor logic correctly overrides zeros and negatives.")

if __name__ == "__main__":
    unittest.main()
