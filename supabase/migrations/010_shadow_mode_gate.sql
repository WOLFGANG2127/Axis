ALTER TABLE virtual_portfolios
ADD COLUMN IF NOT EXISTS fill_realism_audit_passed BOOLEAN DEFAULT FALSE NOT NULL;
