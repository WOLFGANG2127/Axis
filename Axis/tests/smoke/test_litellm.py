import os
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

def run_test(provider_name: str, model: str, api_key_env: str, extra_env: dict | None = None):
    api_key = os.getenv(api_key_env)
    if not api_key:
        raise ValueError(f"{api_key_env} not found in .env")

    print(f"\n=== {provider_name} ===")
    print(f"{api_key_env} Loaded: Yes")

    kwargs = {"api_key": api_key}
    if extra_env:
        kwargs.update(extra_env)

    response = completion(
        model=model,
        messages=[{"role": "user", "content": f"Reply with exactly: {provider_name} Working"}],
        **kwargs
    )

    print(response.choices[0].message["content"])

# 1) Gemini
run_test(
    provider_name="Gemini",
    model="gemini/gemini-2.5-flash",
    api_key_env="GOOGLE_API_KEY"
)

# 2) Groq
run_test(
    provider_name="Groq",
    model="groq/llama-3.3-70b-versatile",
    api_key_env="GROQ_API_KEY"
)

# 3) OpenRouter
run_test(
    provider_name="OpenRouter",
    model="openrouter/openrouter/free",
    api_key_env="OPENROUTER_API_KEY"
)