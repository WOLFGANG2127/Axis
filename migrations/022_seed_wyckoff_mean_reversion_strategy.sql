-- ============================================================================
-- 022_seed_wyckoff_mean_reversion_strategy.sql
-- Phase 2: Strategy #2 database registration.
--
-- This data migration represents the manual Phase 5 approval outcome for the
-- built strategy module after AST scan/review. Runtime status is active so the
-- registry can load it; governance gate modes are recorded as SHADOW in the
-- changelog, matching the new-strategy safety rule.
-- ============================================================================

INSERT INTO strategies (strategy_id, display_name, version, status, source)
VALUES (
    'wyckoff_mean_reversion',
    'Wyckoff Mean Reversion',
    1,
    'active',
    'uploaded'
)
ON CONFLICT (strategy_id) DO UPDATE
SET
    display_name = EXCLUDED.display_name,
    version = EXCLUDED.version,
    status = EXCLUDED.status,
    source = EXCLUDED.source,
    updated_at = NOW();

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
        'wyckoff_mean_reversion',
        'NIFTY',
        2.0,
        0.15,
        2.0,
        100000,
        'default',
        '["candles", "volume_profile", "order_flow", "market_structure"]'::jsonb,
        '{"volume_expansion_ratio": 1.4, "stop_buffer_pct": 0.0015, "target_buffer_pct": 0.0025}'::jsonb,
        15
    ),
    (
        'wyckoff_mean_reversion',
        'BANKNIFTY',
        2.0,
        0.15,
        2.0,
        100000,
        'default',
        '["candles", "volume_profile", "order_flow", "market_structure"]'::jsonb,
        '{"volume_expansion_ratio": 1.4, "stop_buffer_pct": 0.0015, "target_buffer_pct": 0.0025}'::jsonb,
        15
    )
ON CONFLICT (strategy_id, symbol) DO UPDATE
SET
    rr_floor = EXCLUDED.rr_floor,
    stop_buffer_pct = EXCLUDED.stop_buffer_pct,
    position_size_pct_cap = EXCLUDED.position_size_pct_cap,
    paper_capital_allocated = EXCLUDED.paper_capital_allocated,
    alert_template = EXCLUDED.alert_template,
    required_indicators = EXCLUDED.required_indicators,
    entry_parameters = EXCLUDED.entry_parameters,
    margin_buffer_pct = EXCLUDED.margin_buffer_pct,
    updated_at = NOW();

INSERT INTO strategy_config_changelog (
    strategy_id,
    symbol,
    field_changed,
    old_value,
    new_value,
    change_type,
    changed_by,
    details
)
VALUES (
    'wyckoff_mean_reversion',
    NULL,
    'status',
    '"pending_review"'::jsonb,
    '"active"'::jsonb,
    'status_change',
    'codex_phase_2_seed',
    '{
        "security_scan": "passed",
        "manual_review": "required_before_live_capital",
        "governance_gate_modes": {
            "DAILY_LOSS_BREAKER": "SHADOW",
            "RR_FILTER": "SHADOW",
            "CROSS_SYMBOL_CORRELATION": "SHADOW"
        },
        "governance_note": "newly activated strategy gates start in SHADOW"
    }'::jsonb
);

