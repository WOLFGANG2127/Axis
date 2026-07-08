"""
test_cognee_groq.py
===================
End-to-end Cognee pipeline using Groq (free, high-limit) + fastembed (local, no API key).

Use this to verify the full remember()/recall() pipeline without hitting
Gemini free-tier rate limits.

LLM:       groq/llama-3.3-70b-versatile  (6000 tokens/min free tier on Groq)
Embedding: fastembed / BAAI/bge-small-en-v1.5  (local, no API key, 384-dim)
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
load_dotenv(override=True)

groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    print("ERROR: GROQ_API_KEY is not set in .env", file=sys.stderr)
    sys.exit(1)

import cognee

# LLM: Groq with Llama 3.3 70B (high free-tier quota)
# LiteLLM routes "groq/..." to https://api.groq.com/openai/v1 automatically.
# Using provider="custom" would require endpoint + "openai/" prefix on the model.
cognee.config.set_llm_provider("custom")
cognee.config.set_llm_endpoint("https://api.groq.com/openai/v1")
# For the custom/OpenAI-compat path, LiteLLM needs the model prefixed with "openai/"
cognee.config.set_llm_model("openai/llama-3.3-70b-versatile")
cognee.config.set_llm_api_key(groq_key)

# Embeddings: fastembed (local, zero API calls, zero quota)
cognee.config.set_embedding_provider("fastembed")
cognee.config.set_embedding_model("BAAI/bge-small-en-v1.5")
cognee.config.set_embedding_dimensions(384)

DATASET = "axis_groq_test"


async def main():
    print("=" * 60)
    print("Starting remember()  [Groq LLM + fastembed]")
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
