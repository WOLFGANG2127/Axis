import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("❌ OPENROUTER_API_KEY not found in .env")

print("✅ OPENROUTER_API_KEY Loaded")

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="openrouter/free",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: OpenRouter API Working"
        }
    ]
)

print("=" * 60)
print(response.choices[0].message.content)
print("=" * 60)