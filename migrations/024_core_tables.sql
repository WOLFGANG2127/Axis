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
