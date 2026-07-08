"""
test_cognee_litellm.py
======================
End-to-end Cognee smoke test using Google AI Studio (Gemini) via LiteLLM.

Key rules for LiteLLM → Gemini AI Studio routing:
  - Model must have "gemini/" prefix  →  gemini provider (API-key auth)
  - Model WITHOUT prefix              →  vertex_ai provider (ADC / GCP auth) ← WRONG

The .env must contain:
  GEMINI_API_KEY   = <your Google AI Studio key>   (LiteLLM env-var fallback)
  LLM_PROVIDER     = gemini
  LLM_MODEL        = gemini/gemini-2.5-flash        (gemini/ prefix is mandatory)
  LLM_API_KEY      = <same Google AI Studio key>    (Cognee's LLMConfig field)
  EMBEDDING_PROVIDER = gemini
  EMBEDDING_MODEL    = gemini/gemini-embedding-001   (gemini/ prefix is mandatory)
  EMBEDDING_API_KEY  = <same Google AI Studio key>
"""

import asyncio
import os
import sys

# ── 1. Load .env BEFORE importing cognee (cognee.__init__ also loads it, but
#       we want our os.environ values to win in case of override conflicts) ──
from dotenv import load_dotenv
load_dotenv(override=True)

# ── 2. Sanity check: ensure GEMINI_API_KEY is present ──────────────────────
google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not google_key:
    print("ERROR: Neither GOOGLE_API_KEY nor GEMINI_API_KEY is set in .env", file=sys.stderr)
    sys.exit(1)

# Guarantee GEMINI_API_KEY is in os.environ so LiteLLM's internal env-var
# lookup also succeeds (it checks GEMINI_API_KEY as a fallback).
os.environ.setdefault("GEMINI_API_KEY", google_key)

# ── 3. Import cognee AFTER env is loaded ───────────────────────────────────
import cognee

# ── 4. Runtime config (belt + suspenders on top of .env bootstrap) ─────────
# -----------------------
# Configure Stable Hybrid Config (Groq LLM + Gemini Embeddings)
# -----------------------
# Gemini free tier has a 5 RPM limit on gemini-2.5-flash which breaks Cognee's
# multi-step graph extraction. We use Groq for LLM tasks (high speed, higher RPM)
# and Gemini exclusively for embeddings (few requests).
cognee.config.set_llm_provider("groq")
cognee.config.set_llm_model("groq/llama-3.3-70b-versatile")
cognee.config.set_llm_api_key(os.getenv("GROQ_API_KEY"))

cognee.config.set_embedding_provider("gemini")
# Use gemini-embedding-001 as text-embedding-004 raises 'Not Found' in AI Studio v1beta embedding currently
cognee.config.set_embedding_model("gemini/gemini-embedding-001")
cognee.config.set_embedding_api_key(os.getenv("GOOGLE_API_KEY"))

# ── 5. Dataset name ────────────────────────────────────────────────────────
DATASET = "axis_test"

# ── 6. Main pipeline ───────────────────────────────────────────────────────
async def main():
    print("=" * 60)
    print("Starting remember()...")
    print("=" * 60)

    await cognee.remember(
        [
            r"data\knowledge\trap_mechanism.txt",
            r"data\knowledge\wyckoff.txt",
            r"data\knowledge\vsa.txt",
        ],
        dataset_name=DATASET,
        self_improvement=False,
    )

    print()
    print("remember() completed successfully.")
    print()
    print("=" * 60)
    print("Starting recall()...")
    print("=" * 60)

    result = await cognee.recall(
        "Explain Wyckoff accumulation.",
        datasets=[DATASET],
        top_k=3,
    )

    print()
    print("recall() results:")
    if result:
        for i, item in enumerate(result, 1):
            print(f"\n--- Result {i} ---")
            print(item)
    else:
        print("(no results returned)")

    print()
    print("=" * 60)
    print("Pipeline complete.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())