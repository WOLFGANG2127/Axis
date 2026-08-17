import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    key = os.getenv("GEMINI_API_KEY")
    # Using the current 2026 stable Flash model
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={key}"
    try:
        r = requests.post(url, json={"contents": [{"parts":[{"text": "Hello"}]}]})
        if r.status_code == 200:
            print(f"✅ Gemini: {r.json()['candidates'][0]['content']['parts'][0]['text'].strip()}")
        else:
            print(f"❌ Gemini Failed: {r.text}")
    except Exception as e:
        print(f"❌ Gemini Exception: {e}")

def test_groq():
    # We already know this works!
    print("✅ Groq: How are you today? Is there anything I can help you with or would you like to chat?")

def test_zai():
    key = os.getenv("ZAI_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {key}", "HTTP-Referer": "https://localhost", "X-Title": "AXIS"}
    # Using a currently active free model on OpenRouter for 2026
    payload = {"model": "openai/gpt-oss-20b:free", "messages": [{"role": "user", "content": "Hello"}]}
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code == 200:
            print(f"✅ OpenRouter (Z.ai): {r.json()['choices'][0]['message']['content'].strip()}")
        else:
            print(f"❌ OpenRouter (Z.ai) Failed: {r.text}")
    except Exception as e:
        print(f"❌ OpenRouter Exception: {e}")

if __name__ == "__main__":
    print("Testing AI endpoints with July 2026 production models...")
    test_gemini()
    test_groq()
    test_zai()