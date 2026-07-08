import asyncio
import os
import sys

from dotenv import load_dotenv
load_dotenv(override=True)

import cognee
from cognee.infrastructure.llm.LLMGateway import LLMGateway
from cognee.infrastructure.session.feedback_models import SessionTurnAnalysis

cognee.config.set_llm_provider("custom")
cognee.config.set_llm_endpoint("https://api.groq.com/openai/v1")
cognee.config.set_llm_model("openai/llama-3.3-70b-versatile")
cognee.config.set_llm_api_key(os.getenv("GROQ_API_KEY"))

async def main():
    try:
        result = await LLMGateway.acreate_structured_output(
            "CURRENT USER MESSAGE:\\nExplain Wyckoff accumulation.",
            "You analyze one user message... Set query_to_answer...",
            SessionTurnAnalysis
        )
        print("Success!")
        print(result)
    except Exception as e:
        print("Exception:", type(e).__name__)
        print(e)

if __name__ == "__main__":
    asyncio.run(main())
