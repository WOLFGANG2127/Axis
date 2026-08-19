import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

sb = create_client(url, key)
sb.table("system_paused").update({"is_paused": True, "paused_by": "manual-audit-lockdown", "paused_reason": "debugging in progress"}).eq("id", 1).execute()

res = sb.table("system_paused").select("*").execute()
print("SYSTEM PAUSED RESULT:", res.data)
