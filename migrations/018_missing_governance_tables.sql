-- ============================================================================
-- 018_missing_governance_tables.sql
-- DBG-E1 Fix: Creates tables referenced in code but absent from prior migrations.
-- Safe to re-run: all operations use IF NOT EXISTS / IF NOT EXISTS patterns.
-- ============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. trader_session_state
--    Tracks per-day, per-symbol session-level risk state.
--    Consumed by: prs_quiz.py, telegram_webhook.py (cooling-off override),
--                 risk_manager.py (daily loss breaker).
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS trader_session_state (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    trading_date    DATE        NOT NULL,
    symbol          TEXT        NOT NULL DEFAULT 'ALL',
    strategy_name   TEXT        NOT NULL DEFAULT 'ALL',

    -- Daily loss tracking (flat frequency + magnitude)
    daily_loss_count    INTEGER     NOT NULL DEFAULT 0,
    daily_rupee_loss    NUMERIC     NOT NULL DEFAULT 0.0,

    -- Circuit breaker / cooling-off
    circuit_breaker_triggered  BOOLEAN   NOT NULL DEFAULT FALSE,
    cooling_off_until          TIMESTAMPTZ,

    -- Capital snapshot at session open (for drawdown % calculation)
    session_start_capital      NUMERIC   NOT NULL DEFAULT 0.0,

    -- PRS (Personal Readiness Score)
    prs_score              INTEGER   DEFAULT 0,
    prs_completed          BOOLEAN   DEFAULT FALSE,
    is_trading_blocked     BOOLEAN   NOT NULL DEFAULT FALSE,

    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Prevent duplicate rows for the same date+symbol+strategy
    CONSTRAINT uq_session_state_date_sym_strat
        UNIQUE (trading_date, symbol, strategy_name)
);

-- Primary query pattern: lookup by trading_date + symbol + strategy_name
CREATE INDEX IF NOT EXISTS idx_tss_date_symbol_strategy
    ON trader_session_state (trading_date, symbol, strategy_name);

-- Secondary: filter blocked sessions
CREATE INDEX IF NOT EXISTS idx_tss_blocked
    ON trader_session_state (trading_date)
    WHERE is_trading_blocked = TRUE;

ALTER TABLE trader_session_state ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'trader_session_state'
          AND policyname = 'Allow service_role full access to trader_session_state'
    ) THEN
        CREATE POLICY "Allow service_role full access to trader_session_state"
            ON trader_session_state
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;


-- ─────────────────────────────────────────────────────────────────────────────
-- 2. macro_regime_flags
--    Cross-symbol correlation signals written by verifier_node, read by the
--    other symbol's verifier_node in the same 5-minute window.
--    Consumed by: nodes.py (lines 254-294).
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS macro_regime_flags (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    signal_timestamp  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    symbol            TEXT        NOT NULL,
    direction         TEXT        NOT NULL,
    session_id        TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Primary query: other symbol's most-recent flag within the last 60 minutes
CREATE INDEX IF NOT EXISTS idx_mrf_timestamp_symbol_direction
    ON macro_regime_flags (signal_timestamp DESC, symbol, direction);

ALTER TABLE macro_regime_flags ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'macro_regime_flags'
          AND policyname = 'Allow service_role full access to macro_regime_flags'
    ) THEN
        CREATE POLICY "Allow service_role full access to macro_regime_flags"
            ON macro_regime_flags
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;


-- ─────────────────────────────────────────────────────────────────────────────
-- 3. governance_actions
--    Immutable audit trail for every governance gate evaluation.
--    Every signal that reaches verifier_node should produce at least one row
--    here, even in SHADOW mode (would_block=TRUE, did_block=FALSE).
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS governance_actions (
    id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    timestamp    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    gate_name    TEXT        NOT NULL,          -- e.g. 'RR_FILTER', 'DAILY_LOSS_BREAKER', 'PRS_GATE'
    mode         TEXT        NOT NULL DEFAULT 'SHADOW',  -- 'SHADOW', 'ENFORCE', 'OFF'
    would_block  BOOLEAN     NOT NULL DEFAULT FALSE,
    did_block    BOOLEAN     NOT NULL DEFAULT FALSE,
    reason       TEXT,                          -- human-readable explanation
    signal_id    TEXT,                          -- links back to the signal being evaluated
    details      JSONB       DEFAULT '{}',     -- arbitrary structured context
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Lookup by signal (post-mortem analysis)
CREATE INDEX IF NOT EXISTS idx_ga_signal_id
    ON governance_actions (signal_id);

-- Time-range scans (daily governance dashboard)
CREATE INDEX IF NOT EXISTS idx_ga_timestamp
    ON governance_actions (timestamp DESC);

-- Filter by gate for mode audits
CREATE INDEX IF NOT EXISTS idx_ga_gate_mode
    ON governance_actions (gate_name, mode);

ALTER TABLE governance_actions ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'governance_actions'
          AND policyname = 'Allow service_role full access to governance_actions'
    ) THEN
        CREATE POLICY "Allow service_role full access to governance_actions"
            ON governance_actions
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;


-- ─────────────────────────────────────────────────────────────────────────────
-- 4. trade_outcomes.signal_metadata
--    JSONB column for flexible signal-time + outcome-time metadata.
--    Written by: nodes.py (signal time), outcome_recorder.py (outcome time).
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE trade_outcomes
    ADD COLUMN IF NOT EXISTS signal_metadata JSONB;


-- ─────────────────────────────────────────────────────────────────────────────
-- 5. trade_tags index (audit finding from 016_governance_core.sql review)
--    trade_tags.trade_id has no index — queries by trade_id will full-scan.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_trade_tags_trade_id
    ON trade_tags (trade_id);


-- ============================================================================
-- Done. Verify with:
--   SELECT tablename FROM pg_tables WHERE schemaname = 'public'
--     AND tablename IN ('trader_session_state','macro_regime_flags','governance_actions');
-- ============================================================================
