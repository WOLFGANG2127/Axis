import os
import requests

def test_rpc():
    supabase_url = "https://siutlouqtpzppavyvqoj.supabase.co"
    service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNpdXRsb3VxdHB6cHBhdnl2cW9qIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MzA4MTY5MiwiZXhwIjoyMDk4NjU3NjkyfQ.tPGlP1lHLlkUFZ1cpkn9W7lv0pCYyyZfNZJiJ7LI0I8"
    
    headers = {
        "apikey": service_key,
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/json"
    }
    
    sql = """
    alter table strategies enable row level security;
    drop policy if exists "public_select" on strategies;
    create policy "public_select" on strategies for select using (true);
    grant select on strategies to anon;
    grant select on mv_strategy_leaderboard to anon;
    """
    
    # Let's try some common RPC names for executing sql if this is a custom supabase setup
    for rpc_name in ["exec_sql", "run_sql", "exec", "execute_sql"]:
        res = requests.post(f"{supabase_url}/rest/v1/rpc/{rpc_name}", headers=headers, json={"query": sql})
        print(f"Trying {rpc_name}: {res.status_code} - {res.text}")
        
    # Also just check strategies to see if service_role can read it
    res_str = requests.get(f"{supabase_url}/rest/v1/strategies?select=*", headers=headers)
    print("Service role read strategies:", len(res_str.json()), "rows")

if __name__ == "__main__":
    test_rpc()
