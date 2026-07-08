import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in .env")

print("✅ GOOGLE_API_KEY Loaded")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Reply with exactly: Gemini API Working"
)

print("=" * 60)
print("Gemini Response:")
print(response.text)
print("=" * 60)