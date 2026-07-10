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
