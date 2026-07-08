import os
from dotenv import load_dotenv

load_dotenv()

# Set environment BEFORE importing Cognee
os.environ["LLM_PROVIDER"] = "gemini"
os.environ["LLM_MODEL"] = "gemini/gemini-2.5-flash"
os.environ["LLM_API_KEY"] = os.getenv("GOOGLE_API_KEY")

os.environ["EMBEDDING_PROVIDER"] = "gemini"
os.environ["EMBEDDING_MODEL"] = "gemini/gemini-embedding-001"
os.environ["EMBEDDING_API_KEY"] = os.getenv("GOOGLE_API_KEY")

import cognee

print("LLM Config:")
print(cognee.config.get_llm_config())

print("\nEmbedding Config:")
print(cognee.config.get_embedding_config())