-- 015_llm_cost_guardrail.sql
-- Migration to track and enforce daily LLM budget spending

CREATE TABLE IF NOT EXISTS llm_cost_guardrail (
    trading_date DATE PRIMARY KEY,
    cumulative_spend_usd NUMERIC NOT NULL DEFAULT 0.0,
    hard_cap_usd NUMERIC NOT NULL DEFAULT 2.00
);

-- Enable Row Level Security (RLS)
ALTER TABLE llm_cost_guardrail ENABLE ROW LEVEL SECURITY;

-- Grant access to service_role (matches the existing backend access pattern)
CREATE POLICY "Allow service_role full access to llm_cost_guardrail"
    ON llm_cost_guardrail
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Create atomic increment RPC function to prevent race conditions
CREATE OR REPLACE FUNCTION increment_llm_spend(
    p_trading_date DATE,
    p_cost_usd NUMERIC,
    p_hard_cap_usd NUMERIC DEFAULT 2.00
)
RETURNS NUMERIC AS $$
DECLARE
    v_new_spend NUMERIC;
BEGIN
    INSERT INTO llm_cost_guardrail (trading_date, cumulative_spend_usd, hard_cap_usd)
    VALUES (p_trading_date, p_cost_usd, p_hard_cap_usd)
    ON CONFLICT (trading_date) 
    DO UPDATE SET 
        cumulative_spend_usd = llm_cost_guardrail.cumulative_spend_usd + EXCLUDED.cumulative_spend_usd
    RETURNING cumulative_spend_usd INTO v_new_spend;
    
    RETURN v_new_spend;
END;
$$ LANGUAGE plpgsql;
