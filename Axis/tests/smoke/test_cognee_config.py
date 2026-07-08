import os
from dotenv import load_dotenv
import cognee

load_dotenv()

cognee.config.set_llm_provider("openrouter")

cognee.config.set_llm_endpoint(
    "https://openrouter.ai/api/v1"
)

cognee.config.set_llm_model(
    "google/gemma-3-27b-it:free"
)

cognee.config.set_llm_api_key(
    os.getenv("OPENROUTER_API_KEY")
)

print("Configuration Complete")