-- =============================================================================
-- 023_rls_strategies.sql
-- Enable public read access for the anon role on the strategies table
-- and the mv_strategy_leaderboard view (used by the Strategy Hub widget).
-- =============================================================================

-- Enable RLS on the strategies table (if not already enabled)
alter table strategies enable row level security;

-- Public SELECT policy – allow all rows to be read by any authenticated user
create policy "public_select" on strategies
    for select
    using (true);

-- Grant the anon role SELECT privileges
grant select on strategies to anon;

-- Grant SELECT on the leaderboard view as well
grant select on mv_strategy_leaderboard to anon;
