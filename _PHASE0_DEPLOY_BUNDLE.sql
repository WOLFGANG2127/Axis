-- ============================================================================
-- _PHASE0_DEPLOY_BUNDLE.sql
-- Combined migrations for Phase 0 deployment
-- Contains: 009, 014, 015, 016, 021, 024
-- ============================================================================

-- ============================================================================
-- migrations/009_broker_tokens.sql
-- ============================================================================
CREATE TABLE IF NOT EXISTS broker_tokens (
    id INT PRIMARY KEY DEFAULT 1,
    access_token TEXT NOT NULL,
    generated_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    refresh_method TEXT CHECK (refresh_method IN ('renew', 'generate', 'manual')),
    last_refresh_attempt TIMESTAMPTZ,
    last_refresh_status TEXT,
    CONSTRAINT single_row CHECK (id = 1)
);

-- Revoke public access, grant to service_role only per instructions
REVOKE ALL ON broker_tokens FROM anon;
GRANT INSERT, UPDATE, SELECT, DELETE ON broker_tokens TO service_role;

-- ============================================================================
-- migrations/014_api_circuit_breakers.sql
-- ============================================================================
-- 014_api_circuit_breakers.sql
-- Migration to track distributed API circuit breaker states

CREATE TABLE IF NOT EXISTS api_circuit_breakers (
    endpoint TEXT PRIMARY KEY,
    consecutive_failures INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'CLOSED',
    last_failure_at TIMESTAMPTZ,
    CONSTRAINT status_check CHECK (status IN ('CLOSED', 'OPEN'))
);

-- Enable Row Level Security (RLS)
ALTER TABLE api_circuit_breakers ENABLE ROW LEVEL SECURITY;

-- Grant access to service_role (matches the existing backend access pattern)
CREATE POLICY "Allow service_role full access to api_circuit_breakers"
    ON api_circuit_breakers
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- ============================================================================
-- migrations/015_llm_cost_guardrail.sql
-- ============================================================================
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

-- ============================================================================
-- migrations/016_governance_core.sql
-- ============================================================================
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

-- ============================================================================
-- migrations/021_ohlc_candles.sql
-- ============================================================================
-- ============================================================================
-- 021_ohlc_candles.sql
-- D-007 / Phase 2.5: persisted candle relay.
--
-- Stores the exact OHLC rows already fetched by the backend cycle via Dhan.
-- Deliberately does not introduce a second quote/charting data source.
-- Idempotent: safe to re-run; all CREATE/ALTER statements use IF NOT EXISTS
-- and DO $$ BEGIN ... IF NOT EXISTS ... END $$ guards.
-- ============================================================================

CREATE TABLE IF NOT EXISTS ohlc_candles (
    symbol           TEXT NOT NULL CHECK (symbol IN ('NIFTY', 'BANKNIFTY')),
    interval         TEXT NOT NULL DEFAULT '5',
    "timestamp"      TIMESTAMPTZ NOT NULL,
    open             NUMERIC NOT NULL,
    high             NUMERIC NOT NULL,
    low              NUMERIC NOT NULL,
    close            NUMERIC NOT NULL,
    volume           NUMERIC,
    oi               NUMERIC,
    source           TEXT NOT NULL DEFAULT 'dhan',
    trust_status     TEXT NOT NULL DEFAULT 'live'
        CHECK (trust_status IN ('live', 'stale', 'demo-fallback')),
    fetched_at       TIMESTAMPTZ,
    cycle_timestamp  TIMESTAMPTZ,
    correlation_id   TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (symbol, interval, "timestamp")
);

CREATE INDEX IF NOT EXISTS idx_ohlc_candles_symbol_time
    ON ohlc_candles (symbol, "timestamp" DESC);

CREATE INDEX IF NOT EXISTS idx_ohlc_candles_cycle
    ON ohlc_candles (correlation_id)
    WHERE correlation_id IS NOT NULL;

ALTER TABLE ohlc_candles ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'ohlc_candles'
          AND policyname = 'Allow service_role full access to ohlc_candles'
    ) THEN
        CREATE POLICY "Allow service_role full access to ohlc_candles"
            ON ohlc_candles
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'ohlc_candles'
          AND policyname = 'Allow authenticated read access to ohlc_candles'
    ) THEN
        CREATE POLICY "Allow authenticated read access to ohlc_candles"
            ON ohlc_candles
            FOR SELECT
            TO authenticated
            USING (true);
    END IF;
END $$;

COMMENT ON TABLE ohlc_candles IS
    'Backend-relayed OHLC candles from the same Dhan feed used by strategy evaluation; no independent chart data source.';

COMMENT ON COLUMN ohlc_candles."timestamp" IS
    'Candle timestamp stored as TIMESTAMPTZ. Backend normalizes naive timestamps as Asia/Kolkata.';

-- ============================================================================
-- migrations/024_core_tables.sql
-- ============================================================================
-- =============================================================================
-- D-011: Core Tier Migration (7 tables)
-- Verbatim from AXIS_MASTER_v11.md Appendix C.
-- Agent 5 will diff this against Appendix C -- do not re-derive from memory.
-- =============================================================================

-- =========================== CORE TIER (build immediately -- 7 tables) ==========

CREATE TABLE IF NOT EXISTS signals (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol              TEXT NOT NULL,
    cycle_timestamp     TIMESTAMPTZ NOT NULL,
    correlation_id      TEXT,
    direction_score     INTEGER,
    structure_confirmed BOOLEAN,
    active_strategy_slug TEXT,
    analyst_opinion     JSONB,
    verdict             JSONB,
    dedup_status        TEXT,
    alert_sent          BOOLEAN NOT NULL DEFAULT false,
    telegram_sent       BOOLEAN NOT NULL DEFAULT false,   -- D-048
    telegram_error      TEXT,                              -- D-048
    is_backtest         BOOLEAN NOT NULL DEFAULT false,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_signals_symbol_cycle ON signals (symbol, cycle_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_signals_unsent ON signals (telegram_sent) WHERE telegram_sent = false;  -- D-048 retry query
CREATE INDEX IF NOT EXISTS idx_signals_dedup ON signals (symbol, active_strategy_slug, cycle_timestamp DESC);  -- D-049

CREATE TABLE IF NOT EXISTS active_position (          -- D-050
    symbol              TEXT PRIMARY KEY,
    strike              NUMERIC,
    option_type         TEXT CHECK (option_type IN ('CE','PE')),
    entry_price         NUMERIC,
    opened_at           TIMESTAMPTZ,
    signal_id           UUID REFERENCES signals(id) ON DELETE SET NULL,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS system_paused (             -- singleton kill switch, fail-CLOSED per D-T8
    id                  INTEGER PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    is_paused           BOOLEAN NOT NULL DEFAULT true,  -- fail-closed at the SCHEMA level too,
                                                          -- not just on a read failure -- v11 hardening
    paused_by           TEXT,
    paused_reason       TEXT,
    paused_at           TIMESTAMPTZ,
    resumed_at          TIMESTAMPTZ
);
INSERT INTO system_paused (id, is_paused) VALUES (1, true) ON CONFLICT (id) DO NOTHING;
-- A fresh deploy starts PAUSED. Flip to false deliberately (A§6.1's checklist) once you're
-- actually ready for Phase 1 -- never let "the migration ran" double as "start trading."

CREATE TABLE IF NOT EXISTS telegram_updates_processed (   -- NEW in v11, supports D-055
    update_id           BIGINT PRIMARY KEY,
    command              TEXT,
    processed_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- Purpose: Telegram may redeliver the same webhook update on a timeout or retry.
-- The inbound endpoint checks this table before acting; if update_id already exists,
-- it returns 200 immediately without repeating the effect (idempotent command handling,
-- A§2.0 principle 2). One tiny table, closes a real double-execution risk for /record
-- and /close specifically.

CREATE TABLE IF NOT EXISTS trader_session_state (       -- backs /ready
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), session_date DATE NOT NULL UNIQUE,
    is_ready BOOLEAN NOT NULL DEFAULT false,        -- ONE column, fail-closed by default.
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- calendar_gate_node's rule is single-sourced and simple: no row for today, or
-- is_ready = false -> blocked. /ready UPSERTs today's row with is_ready = true.
-- (v11 hardening: this table used to also carry a separate is_trading_blocked
-- column defaulting true, which nothing consistently checked and which could
-- silently disagree with is_ready. One column, one meaning -- A§2.0 principle 3.)

CREATE TABLE IF NOT EXISTS cycle_summaries (           -- D-037 real heartbeat; promoted to
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),      -- Core tier in v11 -- a liveness
    cycle_timestamp TIMESTAMPTZ NOT NULL,                -- signal is a day-one need, not a
    symbols_processed TEXT[], signals_generated INTEGER DEFAULT 0, alerts_sent INTEGER DEFAULT 0,
    status TEXT DEFAULT 'OK' CHECK (status IN ('OK','CRASH','DEGRADED')),  -- used by Phase 3's gate
    errors JSONB DEFAULT '[]', duration_ms INTEGER, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_cycle_summaries_status ON cycle_summaries (status, cycle_timestamp DESC);

CREATE TABLE IF NOT EXISTS macro_regime_flags (        -- Core tier, NOT Extended -- A§2.3 step 8
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(), cycle_timestamp TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL, direction TEXT, haircut_applied BOOLEAN NOT NULL DEFAULT false,
    haircut_pct NUMERIC, correlated_symbol TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_macro_regime_flags_cycle ON macro_regime_flags (cycle_timestamp);
-- v11 correction: this table was originally filed under Extended tier ("build only when
-- the feature that needs it is built"), which was wrong -- the cross-symbol correlation
-- step (A§2.3 step 8) that writes here is NOT optional or deferred, it runs unconditionally
-- every single cycle per A§2.1's own "dispatch deferred until both finish" constraint. Left
-- in Extended tier, the very first cycle where both symbols PROCEED in the same direction
-- would crash on an INSERT into a table that doesn't exist yet. Core tier is 7 tables, not 6.

-- =========================== RLS (enable immediately after creating tables) ======
ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
ALTER TABLE active_position ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_paused ENABLE ROW LEVEL SECURITY;
ALTER TABLE telegram_updates_processed ENABLE ROW LEVEL SECURITY;
ALTER TABLE trader_session_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE cycle_summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE macro_regime_flags ENABLE ROW LEVEL SECURITY;

-- Grant anon SELECT on signals only (dashboard read-only access per A§5.2 step 3a)
DROP POLICY IF EXISTS "anon_read_signals" ON signals;
CREATE POLICY "anon_read_signals" ON signals
    FOR SELECT TO anon USING (true);
-- All other tables: RLS enabled, zero anon policies -- service_role only (backend writes).
