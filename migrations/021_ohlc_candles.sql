-- ============================================================================
-- 021_ohlc_candles.sql
-- Phase 2.5: persisted candle relay for frontend charting.
--
-- This table stores the exact OHLC rows already fetched by the backend cycle.
-- It deliberately does not introduce a second quote/charting data source.
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

