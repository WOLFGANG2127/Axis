-- 016_governance_core.sql
-- Migration to create the foundation for the automated Risk Desk

-- 1. Daily Risk Limits Table (Enforces the Daily Loss Circuit Breaker)
CREATE TABLE IF NOT EXISTS daily_risk_limits (
    trading_date DATE PRIMARY KEY,
    current_drawdown NUMERIC NOT NULL DEFAULT 0.0,
    max_loss_limit NUMERIC NOT NULL DEFAULT 5000.00
);

ALTER TABLE daily_risk_limits ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow service_role full access to daily_risk_limits"
    ON daily_risk_limits
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- 2. Trade Tags Table (For post-mortem analysis and behavioral tracking)
CREATE TABLE IF NOT EXISTS trade_tags (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    trade_id BIGINT NOT NULL,
    tag TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE trade_tags ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow service_role full access to trade_tags"
    ON trade_tags
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- 3. Strategy Asymmetry Table (Enforces strict Risk-to-Reward filters)
CREATE TABLE IF NOT EXISTS strategy_asymmetry (
    strategy_name TEXT PRIMARY KEY,
    min_reward_risk_ratio NUMERIC NOT NULL DEFAULT 2.0,
    enforce_strict_filter BOOLEAN NOT NULL DEFAULT TRUE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE strategy_asymmetry ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow service_role full access to strategy_asymmetry"
    ON strategy_asymmetry
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
