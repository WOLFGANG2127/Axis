CREATE TABLE IF NOT EXISTS infrastructure_locks (
    lock_id TEXT PRIMARY KEY,
    acquired_by TEXT NOT NULL,
    acquired_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL
);

-- Revoke public access, grant to service_role per Phase 8 instructions
REVOKE ALL ON infrastructure_locks FROM anon;
GRANT INSERT, UPDATE, SELECT, DELETE ON infrastructure_locks TO service_role;

-- RPC for atomic lock acquisition with self-healing
CREATE OR REPLACE FUNCTION acquire_infrastructure_lock(
    p_lock_id TEXT,
    p_acquired_by TEXT,
    p_ttl_seconds INT
) RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_acquired BOOLEAN := FALSE;
BEGIN
    INSERT INTO infrastructure_locks (lock_id, acquired_by, acquired_at, expires_at)
    VALUES (
        p_lock_id, 
        p_acquired_by, 
        now(), 
        now() + (p_ttl_seconds || ' seconds')::INTERVAL
    )
    ON CONFLICT (lock_id) DO UPDATE
    SET 
        acquired_by = EXCLUDED.acquired_by,
        acquired_at = EXCLUDED.acquired_at,
        expires_at = EXCLUDED.expires_at
    WHERE infrastructure_locks.expires_at < now();

    IF FOUND THEN
        v_acquired := TRUE;
    END IF;

    RETURN v_acquired;
END;
$$;

-- RPC for safe lock release
CREATE OR REPLACE FUNCTION release_infrastructure_lock(
    p_lock_id TEXT,
    p_acquired_by TEXT
) RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM infrastructure_locks
    WHERE lock_id = p_lock_id AND acquired_by = p_acquired_by;
END;
$$;
