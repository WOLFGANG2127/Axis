import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Missing Supabase credentials")
    sys.exit(1)

sb = create_client(url, key)

print("=== A0 ===")
try:
    res = sb.table("cycle_summaries").select("cycle_timestamp").eq("status", "OK").order("cycle_timestamp", desc=True).limit(1).execute()
    print("MAX OK cycle:", res.data)
except Exception as e: print("A0 error 1:", e)

try:
    res = sb.table("signals").select("created_at").eq("telegram_sent", True).order("created_at", desc=True).limit(1).execute()
    print("MAX sent signal:", res.data)
except Exception as e: print("A0 error 2:", e)

try:
    res = sb.table("cycle_summaries").select("cycle_timestamp,status").order("cycle_timestamp", desc=True).limit(10).execute()
    print("Last 10 cycles:", res.data)
except Exception as e: print("A0 error 3:", e)

print("=== A4 ===")
try:
    res = sb.table("system_paused").select("*").execute()
    print("system_paused:", res.data)
except Exception as e: print("A4 error 1:", e)

try:
    # no trader_session_state check yet, wait let's do it
    res = sb.table("trader_session_state").select("*").execute()
    print("trader_session_state:", res.data)
except Exception as e: print("A4 error 2:", e)

print("=== A5 ===")
try:
    res = sb.table("cycle_summaries").select("cycle_timestamp,status,errors,duration_ms").order("cycle_timestamp", desc=True).limit(20).execute()
    print("Last 20 cycles:", res.data)
except Exception as e: print("A5 error 1:", e)

print("=== A6 ===")
try:
    res = sb.table("signals").select("*").eq("telegram_sent", False).order("created_at", desc=True).limit(10).execute()
    print("Unsent signals:", res.data)
except Exception as e: print("A6 error 1:", e)
