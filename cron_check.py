import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
sb = create_client(url, key)

try:
    res = sb.table("cron.job").select("*").execute()
    print("cron.job:", res.data)
except Exception as e:
    print("cron.job error:", e)

try:
    res = sb.table("cron.job_run_details").select("*").order("start_time", desc=True).limit(30).execute()
    print("cron.job_run_details:", res.data)
except Exception as e:
    print("cron.job_run_details error:", e)
