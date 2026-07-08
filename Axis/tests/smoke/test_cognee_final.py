import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

import cognee
import uuid

# -----------------------
# Configure Stable Hybrid Config (Groq LLM + Gemini Embeddings)
# -----------------------
# Gemini free tier has a 5 RPM limit on gemini-2.5-flash which breaks Cognee's
# multi-step graph extraction. We use Groq for LLM tasks (high speed, higher RPM)
# and Gemini exclusively for embeddings (few requests).
#
# OPTIONAL GEMINI PATH:
# If you acquire a paid Gemini API tier, you can switch back to Gemini LLM by setting:
# cognee.config.set_llm_provider("gemini")
# cognee.config.set_llm_model("gemini/gemini-2.5-flash")
#
# We use 'openai' as the provider alias to bypass Cognee's internal Enum validation
# for Groq, while the 'groq/' model prefix correctly routes LiteLLM to the Groq API.
cognee.config.set_llm_provider("openai")
cognee.config.set_llm_model("groq/llama-3.3-70b-versatile")
cognee.config.set_llm_api_key(os.getenv("GROQ_API_KEY"))

cognee.config.set_embedding_provider("gemini")
# Use gemini-embedding-001 as text-embedding-004 raises 'Not Found' in AI Studio v1beta embedding currently
cognee.config.set_embedding_model("gemini/gemini-embedding-001")
cognee.config.set_embedding_api_key(os.getenv("GOOGLE_API_KEY"))

DATASET = f"axis_test_{uuid.uuid4().hex[:8]}"

import shutil
import site

async def main():
    print(f"Using dataset: {DATASET} to prevent SQLite integrity errors...")
    
    print("Starting remember()...")
    await cognee.remember(
        [
            r"data\knowledge\trap_mechanism.txt",
            r"data\knowledge\wyckoff.txt",
            r"data\knowledge\vsa.txt",
        ],
        dataset_name=DATASET,
        self_improvement=False,
    )
    print("remember() completed successfully!")

    print("\nStarting recall()...")
    result = await cognee.recall(
        "Explain Wyckoff accumulation.",
        datasets=[DATASET],
        top_k=3,
    )
    print("Recall Results:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
