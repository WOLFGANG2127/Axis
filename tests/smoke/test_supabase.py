import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
anon_key = os.getenv("SUPABASE_ANON_KEY")

print("SUPABASE_URL =", repr(url))
print(f"SUPABASE_ANON_KEY Loaded: {'Yes' if anon_key else 'No'}")

if not url or not anon_key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_ANON_KEY in .env")

client = create_client(url, anon_key)

print("✅ Supabase client created successfully.")