-- 017_atomic_circuit_breaker.sql
-- Atomic increment function for API circuit breaker failure counters
-- Prevents race conditions when parallel matrix containers hit the same endpoint

CREATE OR REPLACE FUNCTION increment_circuit_failure(
    p_endpoint TEXT,
    p_threshold INTEGER DEFAULT 3
)
RETURNS INTEGER AS $$
DECLARE
    v_new_count INTEGER;
    v_status TEXT;
BEGIN
    INSERT INTO api_circuit_breakers (endpoint, consecutive_failures, status, last_failure_at)
    VALUES (p_endpoint, 1, 'CLOSED', NOW())
    ON CONFLICT (endpoint) 
    DO UPDATE SET 
        consecutive_failures = api_circuit_breakers.consecutive_failures + 1,
        last_failure_at = NOW()
    RETURNING consecutive_failures INTO v_new_count;
    
    -- Update status based on threshold
    IF v_new_count >= p_threshold THEN
        UPDATE api_circuit_breakers 
        SET status = 'OPEN' 
        WHERE endpoint = p_endpoint;
    END IF;
    
    RETURN v_new_count;
END;
$$ LANGUAGE plpgsql;
