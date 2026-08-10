# Component 05 — Agent Pipeline and Knowledge

## 1. What This Component Is For (plain language, 2-3 sentences)
Provides the LLM routing, light response-parsing helpers, and distributed-lock primitives used when the graph invokes analyst and verifier LLM calls. Separately, the knowledge/recall layer (vector store / Cognee) is referenced by tests and requirements but no clear runtime backend wiring is present in src/ that commits a persistent Cognee backend configuration.

## 2. Files in This Component
- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/llm/router.py (184 lines)
  - One-line purpose: Role-based router that calls Analyst (Gemini primary, Z.ai fallback) and Verifier (Groq) using litellm.acompletion and performs pre-flight budget checks against llm_cost_guardrail in Supabase.
  - Key constants/functions:
    - ANALYST_PRIMARY_MODEL = "gemini/gemini-2.5-flash"
    - ANALYST_FALLBACK_MODEL = "zai/glm-4.5-air"
    - VERIFIER_MODEL = "groq/llama-3.3-70b-versatile"
    - call_llm_router(role, state) — exact provider order for analyst: Gemini → Z.ai (fallback under distributed lock); for verifier: Groq with distributed lock. STATUS: VERIFIED — evidence: read src/llm/router.py lines 12–18 and call logic (lines 147–166, 167–181).

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/llm/distributed_lock.py (46 lines)
  - One-line purpose: Postgres-backed distributed lock facade used to serialize fallback LLM calls and verifier concurrency.
  - Key functions: acquire(lock_id, ttl_seconds=60) -> bool, release(lock_id) -> None implemented via get_supabase_client().rpc calls.
  - STATUS: VERIFIED — evidence: read file showing rpc('acquire_infrastructure_lock') usage.

- Path: C:/Users/avadu/OneDrive/Desktop/Axis.worktrees/axis-component-documentation-setup/src/llm/json_extractor.py (41 lines)
  - One-line purpose: Robustly extract the outermost JSON object from LLM responses (strips fences and trailing commas).
  - STATUS: VERIFIED — evidence: extract_json implementation read and inspected.

- Memory/persistence knowledge code (expected): src/memory/ingest.py, src/memory/recall.py — NOT FOUND in src/ (no matches during repository scan)
  - STATUS: CLAIMED-NOT-SHOWN — evidence: repository grep/view did not return these modules under src/; tests referenced Cognee in tests/smoke but no src wiring was located.

## 3. How It Actually Works (the real internal logic, step by step)
1. Graph analyst_node triggers call_llm_router('analyst', state) when SERVICES.analyst is not provided and active_strategy exists.
2. call_llm_router composes messages with _messages(role, state) and calls _acompletion(model, api_key, messages) — _acompletion performs a Supabase pre-flight budget check (llm_cost_guardrail table), calls litellm.acompletion, and then records completion_cost via db.rpc('increment_llm_spend', ...).
3. If the primary model call fails for the analyst, call_llm_router acquires the zai_api_call lock (distributed_lock.acquire) and retries with ANALYST_FALLBACK_MODEL; it marks payload['fallback_from']='gemini'.
4. The verifier path acquires a groq_agent_two lock before calling Groq verifier; if the lock isn't available `_acompletion` isn't attempted and code returns a synthetic BLOCK verdict.
5. Responses are passed through json_extractor.extract_json to coerce into the canonical payload shape; if parsing fails, verifier role returns BLOCK while analyst returns raw+degraded payload.

LLM provider routing order exactly as coded: Analyst primary → "gemini/gemini-2.5-flash", fallback → "zai/glm-4.5-air" (with lock "zai_api_call"); Verifier → "groq/llama-3.3-70b-versatile" (with lock "groq_agent_two"). STATUS: VERIFIED — evidence: explicit constants and branching in src/llm/router.py.

## 4. Connections — What This Depends On, What Depends On This
- Upstream: AxisState payload passed into LLM router; Supabase for budget guardrails and RPC accounting; API keys in settings (GOOGLE_API_KEY, ZAI_API_KEY, GROQ_API_KEY).
- Downstream: verifier output is used by graph.verifier_node decisions; analyst output is used for human-readable analyst_opinion and for verifier to validate.
- External dependencies: litellm, google-genai (via settings/keys), groq SDK; Supabase for locks and accounting.

## 5. Current Status — What's Actually Working vs. Not
sub-feature | status label | evidence
---|---|---
LLM routing order (Gemini → Z.ai fallback; Groq verifier) | VERIFIED | src/llm/router.py constants and call logic inspected
distributed lock RPC facade present | VERIFIED | src/llm/distributed_lock.py uses get_supabase_client().rpc(...) to acquire/release
json extractor present and robust to fences/trailing commas | VERIFIED | src/llm/json_extractor.py read and inspected
Cognee / vectorstore backend wiring (persistence) | CLAIMED-NOT-SHOWN | requirements include cognee and lancedb, tests reference cognee, but no src/ top-level wiring (e.g., src/memory/ingest.py or src/memory/recall.py) was found in the scanned src/, so the persistent knowledge backend is not verifiably configured in src/
knowledge-graph persistence test run history | BUILT-NOT-RUN | tests/smoke include cognee smoke tests, but pytest collection failed in this offline session due to missing deps — cannot assert whether persistence tests have ever been run in CI

## 6. What's Remaining, Specific to This Component Only
- Add (or point out) the memory/ingest and memory/recall modules or the Cognee wiring in src/ so that the knowledge backend is explicitly configured and can be audited (backend type: lancedb / local vs pgvector).
- Run the Cognee persistence smoke tests in a properly provisioned environment (requires installing cognee/lancedb or pgvector and necessary secrets) and record results here.

## 7. Last Verified
2026-07-26 — commit aabcce72ac767f99149bda30dac255721c784e3b
