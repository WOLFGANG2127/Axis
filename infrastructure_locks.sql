-- Migration to create the infrastructure_locks table for LLM API Concurrency Mutex

CREATE TABLE IF NOT EXISTS public.infrastructure_locks (
    lock_name text PRIMARY KEY,
    acquired_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL
);

-- Enable RLS
ALTER TABLE public.infrastructure_locks ENABLE ROW LEVEL SECURITY;

-- Allow service role full access
CREATE POLICY "Allow service role full access to infrastructure_locks"
ON public.infrastructure_locks 
FOR ALL 
USING (auth.role() = 'service_role');
