ALTER TABLE accuracy_log
ADD COLUMN IF NOT EXISTS weight_pcr_divergence NUMERIC(8,4);
