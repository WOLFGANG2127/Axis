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
