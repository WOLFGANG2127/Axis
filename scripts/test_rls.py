import os
import requests

def test_anon_access():
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in environment variables")

    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    
    res = requests.get(f"{SUPABASE_URL}/rest/v1/strategies?select=*", headers=headers)
    print("Status Code:", res.status_code)
    print("Response:", res.text)

if __name__ == "__main__":
    test_anon_access()
