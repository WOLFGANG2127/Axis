-- 020_prs_gate_state.sql
-- Track A: fail-closed PRS trading gate support.

ALTER TABLE trader_session_state
    ADD COLUMN IF NOT EXISTS prs_completed_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS prs_block_reason TEXT;

COMMENT ON COLUMN trader_session_state.prs_completed_at IS
    'IST-aware timestamp when the trader completed the PRS quiz. Trading gate requires this at or before 09:10 IST.';

COMMENT ON COLUMN trader_session_state.prs_block_reason IS
    'Optional explicit reason the PRS gate blocked trading for the trader-day.';
