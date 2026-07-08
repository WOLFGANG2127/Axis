import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("ZAI_API_KEY")

if not api_key:
    raise ValueError("❌ ZAI_API_KEY not found in .env")

print("✅ ZAI_API_KEY Loaded")

client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

response = client.chat.completions.create(
    model="glm-4.5-air",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: Z.ai API Working"
        }
    ],
    temperature=0
)

print("=" * 60)
print(response.choices[0].message.content)
print("=" * 60)