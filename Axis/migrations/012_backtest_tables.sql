-- Create backtest copies of core operational tables
CREATE TABLE IF NOT EXISTS market_context_snapshots_backtest (LIKE market_context_snapshots INCLUDING ALL);
CREATE TABLE IF NOT EXISTS signals_backtest (LIKE signals INCLUDING ALL);
CREATE TABLE IF NOT EXISTS paper_trades_backtest (LIKE paper_trades INCLUDING ALL);
CREATE TABLE IF NOT EXISTS journal_logs_backtest (LIKE journal_logs INCLUDING ALL);

-- Drop RLS for rapid bulk-inserts during backtests
ALTER TABLE market_context_snapshots_backtest DISABLE ROW LEVEL SECURITY;
ALTER TABLE signals_backtest DISABLE ROW LEVEL SECURITY;
ALTER TABLE paper_trades_backtest DISABLE ROW LEVEL SECURITY;
ALTER TABLE journal_logs_backtest DISABLE ROW LEVEL SECURITY;
