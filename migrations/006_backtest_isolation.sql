create table if not exists public.backtest_signals (
    id uuid primary key default gen_random_uuid(),
    backtest_run_id uuid not null,
    symbol text not null,
    generated_at timestamptz not null,
    strategy_name text not null,
    direction_score smallint,
    structure_gate_passed bool,
    verifier_verdict text check (verifier_verdict in ('PROCEED','BLOCK')),
    ev_rupees numeric(12,2),
    used_live_llm bool default false,
    conditions_met jsonb
);

create table if not exists public.backtest_trades (
    id uuid primary key default gen_random_uuid(),
    backtest_signal_id uuid references public.backtest_signals(id) on delete cascade,
    entry_time timestamptz,
    exit_time timestamptz,
    entry_price_index numeric(10,2),
    exit_price_index numeric(10,2),
    net_pnl_rupees numeric(12,2),
    r_multiple_achieved numeric(6,3),
    exit_reason text
);

grant insert, update on public.backtest_signals, public.backtest_trades
  to service_role;
alter table public.backtest_signals enable row level security;
create policy "anon read access" on public.backtest_signals for select
  to anon using (true);
alter table public.backtest_trades enable row level security;
create policy "anon read access" on public.backtest_trades for select
  to anon using (true);
