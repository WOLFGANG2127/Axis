import os
import requests
import json

def fetch_strategies():
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not SUPABASE_URL or not SERVICE_ROLE_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")

    headers = {
        "apikey": SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    # 1. Fetch exact rows to prove the data exists
    res = requests.get(f"{SUPABASE_URL}/rest/v1/strategies?select=*", headers=headers)
    print("=== DATA INTERROGATION (SERVICE ROLE) ===")
    print("Status Code:", res.status_code)
    try:
        data = res.json()
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("Error parsing JSON:", e)
        print("Raw text:", res.text)
        
    # 2. Fetch using ANON key to prove RLS is blocking
    SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
    if not SUPABASE_ANON_KEY:
        print("\nSUPABASE_ANON_KEY not set, skipping anon RLS test.")
        return

    headers_anon = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
        "Content-Type": "application/json"
    }
    res_anon = requests.get(f"{SUPABASE_URL}/rest/v1/strategies?select=*", headers=headers_anon)
    print("\n=== DATA INTERROGATION (ANON ROLE - RLS TEST) ===")
    print("Status Code:", res_anon.status_code)
    print("Data:", res_anon.text)

if __name__ == "__main__":
    fetch_strategies()
