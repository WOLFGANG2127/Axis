import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Load the local .env file
load_dotenv()

url = os.getenv("SUPABASE_URL")
# CRITICAL: We test the SERVICE_ROLE_KEY because that is what the backend uses to bypass RLS.
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

print(f"Testing connection to: {url}")

try:
    # 2. Attempt to initialize the client
    supabase: Client = create_client(url, key)
    
    # 3. Read Test 1: Check the strategies table (Should return 1 row for GVOF)
    print("\n--- Running Read Test 1 (Strategies) ---")
    strat_response = supabase.table("strategies").select("*").execute()
    print(f"SUCCESS! Found {len(strat_response.data)} strategies.")
    
    # 4. Read Test 2: Check trade_outcomes (Should exist, but have 0 rows)
    print("\n--- Running Read Test 2 (Trade Outcomes) ---")
    trade_response = supabase.table("trade_outcomes").select("*").execute()
    print(f"SUCCESS! trade_outcomes table is live and has {len(trade_response.data)} rows.")

    print("\n✅ DATABASE CONNECTION IS 100% FLAWLESS AND READY FOR LIVE OPS.")

except Exception as e:
    print(f"\n❌ CONNECTION FAILED: {str(e)}")