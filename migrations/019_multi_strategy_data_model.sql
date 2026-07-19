-- ============================================================================
-- 019_multi_strategy_data_model.sql
-- Phase 1: multi-strategy schema contracts and journal partitioning.
--
-- Safe to re-run: uses IF NOT EXISTS patterns where PostgreSQL supports them
-- and DO blocks for policy/trigger creation.
-- ============================================================================

-- --------------------------------------------------------------------------
-- 1. Strategy registry
-- --------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS strategies (
    strategy_id   TEXT PRIMARY KEY,
    display_name  TEXT NOT NULL,
    version       INTEGER NOT NULL DEFAULT 1 CHECK (version >= 1),
    status        TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'pending_review', 'active', 'disabled')),
    source        TEXT NOT NULL DEFAULT 'uploaded'
        CHECK (source IN ('built_in', 'uploaded')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_strategies_slug
        CHECK (strategy_id ~ '^[a-z][a-z0-9_]*$')
);

CREATE INDEX IF NOT EXISTS idx_strategies_status
    ON strategies (status);

ALTER TABLE strategies ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'strategies'
          AND policyname = 'Allow service_role full access to strategies'
    ) THEN
        CREATE POLICY "Allow service_role full access to strategies"
            ON strategies
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;

-- --------------------------------------------------------------------------
-- 2. Per-symbol strategy configuration
-- --------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS strategy_configs (
    strategy_id                 TEXT NOT NULL REFERENCES strategies(strategy_id) ON DELETE CASCADE,
    symbol                      TEXT NOT NULL,
    rr_floor                    NUMERIC NOT NULL DEFAULT 2.0 CHECK (rr_floor > 0),
    stop_buffer_pct             NUMERIC NOT NULL DEFAULT 0.15 CHECK (stop_buffer_pct >= 0),
    position_size_pct_cap       NUMERIC NOT NULL DEFAULT 2.0 CHECK (position_size_pct_cap > 0),
    paper_capital_allocated     NUMERIC NOT NULL DEFAULT 100000 CHECK (paper_capital_allocated >= 0),
    alert_template              TEXT NOT NULL DEFAULT 'default',
    required_indicators         JSONB NOT NULL DEFAULT '[]'::jsonb
        CHECK (jsonb_typeof(required_indicators) = 'array'),
    entry_parameters            JSONB NOT NULL DEFAULT '{}'::jsonb
        CHECK (jsonb_typeof(entry_parameters) = 'object'),
    margin_buffer_pct           NUMERIC NOT NULL DEFAULT 15 CHECK (margin_buffer_pct >= 0),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY (strategy_id, symbol)
);

CREATE INDEX IF NOT EXISTS idx_strategy_configs_symbol
    ON strategy_configs (symbol);

ALTER TABLE strategy_configs ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'strategy_configs'
          AND policyname = 'Allow service_role full access to strategy_configs'
    ) THEN
        CREATE POLICY "Allow service_role full access to strategy_configs"
            ON strategy_configs
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;

-- --------------------------------------------------------------------------
-- 3. Immutable config changelog, including capital lifecycle events
-- --------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS strategy_config_changelog (
    id             BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    strategy_id    TEXT NOT NULL REFERENCES strategies(strategy_id) ON DELETE CASCADE,
    symbol         TEXT,
    field_changed  TEXT NOT NULL,
    old_value      JSONB,
    new_value      JSONB,
    change_type    TEXT NOT NULL DEFAULT 'config_update'
        CHECK (change_type IN ('config_update', 'capital_adjustment', 'activation_seed', 'status_change')),
    changed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    changed_by     TEXT NOT NULL DEFAULT 'system',
    details        JSONB NOT NULL DEFAULT '{}'::jsonb
        CHECK (jsonb_typeof(details) = 'object')
);

CREATE INDEX IF NOT EXISTS idx_strategy_config_changelog_strategy_time
    ON strategy_config_changelog (strategy_id, changed_at DESC);

ALTER TABLE strategy_config_changelog ENABLE ROW LEVEL SECURITY;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies
        WHERE tablename = 'strategy_config_changelog'
          AND policyname = 'Allow service_role full access to strategy_config_changelog'
    ) THEN
        CREATE POLICY "Allow service_role full access to strategy_config_changelog"
            ON strategy_config_changelog
            FOR ALL
            TO service_role
            USING (true)
            WITH CHECK (true);
    END IF;
END $$;

-- --------------------------------------------------------------------------
-- 4. Seed existing built-in strategy without enabling new behavior
-- --------------------------------------------------------------------------
INSERT INTO strategies (strategy_id, display_name, version, status, source)
VALUES ('gvof', 'Golden Zone + Volume Profile + Order Flow', 1, 'active', 'built_in')
ON CONFLICT (strategy_id) DO NOTHING;

INSERT INTO strategy_configs (
    strategy_id,
    symbol,
    rr_floor,
    stop_buffer_pct,
    position_size_pct_cap,
    paper_capital_allocated,
    alert_template,
    required_indicators,
    entry_parameters,
    margin_buffer_pct
)
VALUES
    (
        'gvof',
        'NIFTY',
        2.0,
        0.15,
        2.0,
        100000,
        'default',
        '["gex", "volume_profile", "order_flow", "vix", "initial_balance"]'::jsonb,
        '{"fib_lower": 0.618, "fib_upper": 0.786, "ib_min_range": 50, "target_1_exit_pct": 50}'::jsonb,
        15
    ),
    (
        'gvof',
        'BANKNIFTY',
        2.0,
        0.15,
        2.0,
        100000,
        'default',
        '["gex", "volume_profile", "order_flow", "vix", "initial_balance"]'::jsonb,
        '{"fib_lower": 0.618, "fib_upper": 0.786, "ib_min_range": 50, "target_1_exit_pct": 50}'::jsonb,
        15
    )
ON CONFLICT (strategy_id, symbol) DO NOTHING;

-- --------------------------------------------------------------------------
-- 5. Capital lifecycle guard
--
-- paper_capital_allocated is a target allocation. It seeds portfolio capital
-- only at activation time. Once a live virtual_portfolios row has closed trades,
-- this trigger blocks raw overwrite of paper_capital_allocated and instructs the
-- operator to use a distinct capital_adjustment changelog/reconciliation event.
--
-- Live-schema note: paper_trades does not have to carry its own symbol column.
-- If paper_trades.symbol exists, use it. Otherwise, if paper_trades.signal_id
-- and signals.symbol exist, resolve the symbol through signals. If neither path
-- exists, fall back to a conservative strategy-level closed-trade check.
-- --------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION prevent_active_strategy_capital_overwrite()
RETURNS TRIGGER AS $$
DECLARE
    closed_trade_count INTEGER := 0;
    has_pt_symbol BOOLEAN := FALSE;
    has_pt_signal_id BOOLEAN := FALSE;
    has_pt_status BOOLEAN := FALSE;
    has_signals_symbol BOOLEAN := FALSE;
BEGIN
    IF NEW.paper_capital_allocated IS DISTINCT FROM OLD.paper_capital_allocated THEN
        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'paper_trades'
              AND column_name = 'symbol'
        ) INTO has_pt_symbol;

        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'paper_trades'
              AND column_name = 'signal_id'
        ) INTO has_pt_signal_id;

        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'paper_trades'
              AND column_name = 'status'
        ) INTO has_pt_status;

        SELECT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'signals'
              AND column_name = 'symbol'
        ) INTO has_signals_symbol;

        IF has_pt_symbol THEN
            IF has_pt_status THEN
                EXECUTE '
                    SELECT COUNT(*)
                    FROM paper_trades pt
                    WHERE COALESCE(pt.strategy_id, LOWER(pt.strategy_name), $1) = $1
                      AND pt.symbol = $2
                      AND pt.status = ''CLOSED'''
                INTO closed_trade_count
                USING OLD.strategy_id, OLD.symbol;
            ELSE
                EXECUTE '
                    SELECT COUNT(*)
                    FROM paper_trades pt
                    WHERE COALESCE(pt.strategy_id, LOWER(pt.strategy_name), $1) = $1
                      AND pt.symbol = $2'
                INTO closed_trade_count
                USING OLD.strategy_id, OLD.symbol;
            END IF;
        ELSIF has_pt_signal_id AND has_signals_symbol THEN
            IF has_pt_status THEN
                EXECUTE '
                    SELECT COUNT(*)
                    FROM paper_trades pt
                    JOIN signals s ON s.id = pt.signal_id
                    WHERE COALESCE(pt.strategy_id, LOWER(pt.strategy_name), $1) = $1
                      AND s.symbol = $2
                      AND pt.status = ''CLOSED'''
                INTO closed_trade_count
                USING OLD.strategy_id, OLD.symbol;
            ELSE
                EXECUTE '
                    SELECT COUNT(*)
                    FROM paper_trades pt
                    JOIN signals s ON s.id = pt.signal_id
                    WHERE COALESCE(pt.strategy_id, LOWER(pt.strategy_name), $1) = $1
                      AND s.symbol = $2'
                INTO closed_trade_count
                USING OLD.strategy_id, OLD.symbol;
            END IF;
        ELSE
            -- Conservative fallback: if symbol cannot be resolved from the live
            -- schema, block allocation overwrites once the strategy has any
            -- closed trade. This avoids accidentally resetting live capital.
            IF has_pt_status THEN
                EXECUTE '
                    SELECT COUNT(*)
                    FROM paper_trades pt
                    WHERE COALESCE(pt.strategy_id, LOWER(pt.strategy_name), $1) = $1
                      AND pt.status = ''CLOSED'''
                INTO closed_trade_count
                USING OLD.strategy_id;
            ELSE
                EXECUTE '
                    SELECT COUNT(*)
                    FROM paper_trades pt
                    WHERE COALESCE(pt.strategy_id, LOWER(pt.strategy_name), $1) = $1'
                INTO closed_trade_count
                USING OLD.strategy_id;
            END IF;
        END IF;

        IF closed_trade_count > 0 THEN
            RAISE EXCEPTION
                'paper_capital_allocated cannot be overwritten after closed trades exist for %.%; log a capital_adjustment instead',
                OLD.strategy_id,
                OLD.symbol;
        END IF;

        INSERT INTO strategy_config_changelog (
            strategy_id,
            symbol,
            field_changed,
            old_value,
            new_value,
            change_type,
            changed_by,
            details
        ) VALUES (
            OLD.strategy_id,
            OLD.symbol,
            'paper_capital_allocated',
            to_jsonb(OLD.paper_capital_allocated),
            to_jsonb(NEW.paper_capital_allocated),
            'capital_adjustment',
            'system',
            '{"note": "target allocation changed before closed trades existed; current_capital is not overwritten"}'::jsonb
        );
    END IF;

    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgname = 'trg_strategy_configs_capital_lifecycle'
    ) THEN
        CREATE TRIGGER trg_strategy_configs_capital_lifecycle
            BEFORE UPDATE OF paper_capital_allocated ON strategy_configs
            FOR EACH ROW
            EXECUTE FUNCTION prevent_active_strategy_capital_overwrite();
    END IF;
END $$;

-- --------------------------------------------------------------------------
-- 6. Existing operational tables: add strategy partition keys without renames
-- --------------------------------------------------------------------------
ALTER TABLE signals
    ADD COLUMN IF NOT EXISTS strategy_id TEXT NOT NULL DEFAULT 'gvof',
    ADD COLUMN IF NOT EXISTS strategy_name TEXT NOT NULL DEFAULT 'GVOF';

ALTER TABLE paper_trades
    ADD COLUMN IF NOT EXISTS strategy_id TEXT NOT NULL DEFAULT 'gvof',
    ADD COLUMN IF NOT EXISTS strategy_name TEXT NOT NULL DEFAULT 'GVOF';

ALTER TABLE trade_outcomes
    ADD COLUMN IF NOT EXISTS strategy_id TEXT NOT NULL DEFAULT 'gvof',
    ADD COLUMN IF NOT EXISTS strategy_name TEXT NOT NULL DEFAULT 'GVOF',
    ADD COLUMN IF NOT EXISTS signal_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    ADD COLUMN IF NOT EXISTS custom_fields JSONB NOT NULL DEFAULT '{}'::jsonb;

ALTER TABLE governance_actions
    ADD COLUMN IF NOT EXISTS strategy_id TEXT NOT NULL DEFAULT 'gvof',
    ADD COLUMN IF NOT EXISTS strategy_name TEXT NOT NULL DEFAULT 'GVOF';

UPDATE trade_outcomes
SET signal_metadata = '{}'::jsonb
WHERE signal_metadata IS NULL;

ALTER TABLE trade_outcomes
    ALTER COLUMN signal_metadata SET DEFAULT '{}'::jsonb,
    ALTER COLUMN custom_fields SET DEFAULT '{}'::jsonb;

DO $$
DECLARE
    signal_asset_col TEXT;
    paper_trade_asset_col TEXT;
    has_paper_trade_status BOOLEAN := FALSE;
    has_paper_trade_signal_id BOOLEAN := FALSE;
BEGIN
    -- signals is the canonical asset-bearing table in the current app path.
    -- Dashboard code queries paper_trades with signals(symbol, strategy_name),
    -- so paper_trades may not have its own symbol column.
    SELECT column_name INTO signal_asset_col
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'signals'
      AND column_name IN ('symbol', 'ticker', 'instrument', 'underlying', 'asset', 'index_symbol')
    ORDER BY CASE column_name
        WHEN 'symbol' THEN 1
        WHEN 'ticker' THEN 2
        WHEN 'instrument' THEN 3
        WHEN 'underlying' THEN 4
        WHEN 'asset' THEN 5
        WHEN 'index_symbol' THEN 6
        ELSE 99
    END
    LIMIT 1;

    SELECT column_name INTO paper_trade_asset_col
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name = 'paper_trades'
      AND column_name IN ('symbol', 'ticker', 'instrument', 'underlying', 'asset', 'index_symbol')
    ORDER BY CASE column_name
        WHEN 'symbol' THEN 1
        WHEN 'ticker' THEN 2
        WHEN 'instrument' THEN 3
        WHEN 'underlying' THEN 4
        WHEN 'asset' THEN 5
        WHEN 'index_symbol' THEN 6
        ELSE 99
    END
    LIMIT 1;

    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'paper_trades'
          AND column_name = 'status'
    ) INTO has_paper_trade_status;

    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'paper_trades'
          AND column_name = 'signal_id'
    ) INTO has_paper_trade_signal_id;

    IF signal_asset_col IS NOT NULL THEN
        EXECUTE format(
            'CREATE INDEX IF NOT EXISTS idx_signals_strategy_asset ON signals (strategy_id, %I)',
            signal_asset_col
        );
    ELSE
        CREATE INDEX IF NOT EXISTS idx_signals_strategy ON signals (strategy_id);
    END IF;

    IF paper_trade_asset_col IS NOT NULL AND has_paper_trade_status THEN
        EXECUTE format(
            'CREATE INDEX IF NOT EXISTS idx_paper_trades_strategy_asset_status ON paper_trades (strategy_id, %I, status)',
            paper_trade_asset_col
        );
    ELSIF paper_trade_asset_col IS NOT NULL THEN
        EXECUTE format(
            'CREATE INDEX IF NOT EXISTS idx_paper_trades_strategy_asset ON paper_trades (strategy_id, %I)',
            paper_trade_asset_col
        );
    ELSIF has_paper_trade_signal_id AND has_paper_trade_status THEN
        CREATE INDEX IF NOT EXISTS idx_paper_trades_strategy_signal_status
            ON paper_trades (strategy_id, signal_id, status);
    ELSIF has_paper_trade_signal_id THEN
        CREATE INDEX IF NOT EXISTS idx_paper_trades_strategy_signal
            ON paper_trades (strategy_id, signal_id);
    ELSIF has_paper_trade_status THEN
        CREATE INDEX IF NOT EXISTS idx_paper_trades_strategy_status
            ON paper_trades (strategy_id, status);
    ELSE
        CREATE INDEX IF NOT EXISTS idx_paper_trades_strategy
            ON paper_trades (strategy_id);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_trade_outcomes_strategy
    ON trade_outcomes (strategy_id, strategy_name);

CREATE INDEX IF NOT EXISTS idx_governance_actions_strategy_gate
    ON governance_actions (strategy_id, gate_name, timestamp DESC);

-- --------------------------------------------------------------------------
-- 7. trader_session_state verification helper
--
-- 018 already created strategy_name and unique(trading_date, symbol,
-- strategy_name). This block fails loudly if a deployed database is missing the
-- required columns/constraint shape, instead of letting Phase 1 silently proceed.
-- --------------------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'trader_session_state'
          AND column_name = 'strategy_name'
    ) THEN
        RAISE EXCEPTION 'trader_session_state.strategy_name is required before Phase 1 can proceed';
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint c
        JOIN pg_class t ON t.oid = c.conrelid
        WHERE t.relname = 'trader_session_state'
          AND c.contype = 'u'
          AND pg_get_constraintdef(c.oid) ILIKE '%trading_date%'
          AND pg_get_constraintdef(c.oid) ILIKE '%symbol%'
          AND pg_get_constraintdef(c.oid) ILIKE '%strategy_name%'
    ) THEN
        RAISE EXCEPTION 'trader_session_state must be uniquely keyed by trading_date, symbol, strategy_name';
    END IF;
END $$;

-- --------------------------------------------------------------------------
-- 8. AI reasoning catch-all
--
-- Live precheck returned no signal_metadata table. Therefore the flexible
-- catch-all lives on trade_outcomes.custom_fields and trade_outcomes.signal_metadata,
-- preserving the existing journal path and avoiding a new parallel data system.
-- --------------------------------------------------------------------------
COMMENT ON COLUMN trade_outcomes.custom_fields IS
    'Flexible JSONB catch-all for strategy-specific telemetry and AI reasoning payloads.';

COMMENT ON COLUMN trade_outcomes.signal_metadata IS
    'Signal-time and outcome-time metadata populated by verifier/outcome recorder.';

-- ============================================================================
-- Review probes:
--   SELECT strategy_id, display_name, status, source FROM strategies;
--   SELECT strategy_id, symbol, rr_floor, paper_capital_allocated FROM strategy_configs;
--   SELECT column_name, data_type FROM information_schema.columns
--     WHERE table_name = 'trade_outcomes'
--       AND column_name IN ('strategy_id','strategy_name','signal_metadata','custom_fields');
-- ============================================================================
