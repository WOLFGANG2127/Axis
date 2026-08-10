# Component 02 — Data Pipeline

## 1. What This Component Is For (plain language, 2-3 sentences)
Collects market data (candles, option chains) from Dhan, wraps every collector response in a uniform envelope ({data,fetched_at,trust_status}), applies a circuit-breaker for unreliable endpoints, and records circuit state in Postgres via Supabase. This pipeline supplies the scoring layers with "chain" and five-minute-candle inputs.

## 2. Files in This Component
- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/data/dhan_client.py (349 lines)
  - One-line purpose: Dhan v2 market-data client exposing get_candles, get_option_chain, get_expiry_list, token renew/generate helpers.
  - Key functions/classes:
    - _envelope(data, trust_status='live') -> dict: wraps payload with {data, fetched_at, trust_status}
      - STATUS: VERIFIED — evidence: function _envelope present in file.
    - _can_proceed(endpoint) -> bool: checks Postgres api_circuit_breakers row; returns False if OPEN + last failure <5min
      - STATUS: VERIFIED — evidence: code queries api_circuit_breakers via Supabase client (lines show select and time comparison).
    - _record_failure/_record_success: update circuit counters via RPC/upsert (Postgres-backed)
      - STATUS: VERIFIED — evidence: calls to client.rpc('increment_circuit_failure') and upsert present in file.
    - get_candles/get_option_chain/get_expiry_list: actual HTTP calls to Dhan endpoints with header building from broker_tokens
      - STATUS: VERIFIED — evidence: functions call f"{DHAN_API}/{endpoint}" and use _headers() which reads broker_tokens from DB.
    - renew_token, generate_access_token, generate_totp: token lifecycle helpers used by token_refresher
      - STATUS: VERIFIED — evidence: functions present and used by src/scheduling/token_refresher.py

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/scheduling/token_refresher.py (114 lines)
  - One-line purpose: Periodic token lifecycle manager that prefers RenewToken then falls back to generate_access_token and upserts broker_tokens row.
  - Key functions/classes: refresh_if_needed() — RenewToken-first, generate_access_token fallback, sets new expires_at = now + 24h
  - STATUS: VERIFIED — evidence: token_refresher.py lines show try/except where renew_token() is attempted first, then generate_access_token() on exception; GitHub Actions workflow schedules this job.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/.github/workflows/token_refresh.yml (71 lines)
  - One-line purpose: Cron-run GitHub Action that runs the token refresher every 8 hours (cron: '0 */8 * * *')
  - STATUS: VERIFIED — evidence: workflow file includes schedule and runs refresh_if_needed via python -c invocation.

## 3. How It Actually Works (the real internal logic, step by step)
1. Each collector (e.g., get_candles/get_option_chain) performs a _can_proceed pre-flight check that queries api_circuit_breakers in Postgres to see if the endpoint is OPEN and recently failed; if so, it returns None as a safe default.
2. If allowed, the collector builds headers by reading the broker_tokens table (get active access_token), calls the Dhan HTTP endpoint via httpx, then runs _raise_for_api_error(response) and on success calls _record_success(endpoint) which upserts the breaker closed.
3. On exception the collector calls _record_failure(endpoint) which increments the failure counter via an RPC that trips at _CIRCUIT_THRESHOLD (3) and triggers a Telegram alert.
4. Token refresh flow: src/scheduling/token_refresher.refresh_if_needed reads broker_tokens.id=1 row; if expires_at < now + 2h, it tries renew_token() first and falls back to generate_access_token(pin, totp) on exception; then upserts the new token (refresh_method set to 'renew' or 'generate'). The GitHub Action runs refresh_if_needed every 8 hours.
5. Data envelope shape is explicitly enforced by _envelope(data, trust_status) returning {"data":..., "fetched_at":iso, "trust_status":...}, and this envelope is used by get_candles and get_option_chain.

## 4. Connections — What This Depends On, What Depends On This
- Upstream: Dhan API endpoints (DHAN_API), broker_tokens table in Supabase, environment settings (DHAN_CLIENT_ID, secrets). The token_refresher relies on SUPABASE env secrets configured in GitHub Actions.
- Downstream: scoring modules (src/scoring/*) expect chain payloads and the envelope shape; graph nodes call data verification which persists OHLC via persist_ohlc_candles.
- External dependencies: network access to api.dhan.co; Supabase/Postgres access for tokens and circuit state; environment variables (SUPABASE_* and DHAN_*).

## 5. Current Status — What's Actually Working vs. Not
sub-feature | status label | evidence
---|---|---
collector functions present (get_candles, get_option_chain) | VERIFIED | src/data/dhan_client.py inspected
uniform envelope {data,fetched_at,trust_status} | VERIFIED | _envelope function present and used in collectors
circuit-breaker pre-flight and storage | VERIFIED | _can_proceed and _record_failure/_record_success exist and call Supabase
RenewToken-first then generate fallback schedule | VERIFIED | src/scheduling/token_refresher.py and .github/workflows/token_refresh.yml show logic and schedule
observed NSE fallback usage (has NSE fallback ever been observed against live market data?) | UNABLE TO QUERY LIVE DB / RUNTIME NETWORK (Offline Workspace Scan) | no live Dhan network calls executed from this offline workspace; cannot observe historical fallback events here

## 6. What's Remaining, Specific to This Component Only
- Confirm in a live environment whether the circuit-breaker has ever opened for Dhan endpoints and whether generator fallback (generate_access_token) has been exercised — requires live Supabase & network access.
- Document the frequency of renew vs generate in broker_tokens table (refresh_method) from live DB history.

## 7. Last Verified
2026-07-26 — commit aabcce72ac767f99149bda30dac255721c784e3b
