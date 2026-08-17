import os
import requests

def test_rpc():
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not SUPABASE_URL or not SERVICE_ROLE_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables")

    headers = {
        "apikey": SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SERVICE_ROLE_KEY}",
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
        res = requests.post(f"{SUPABASE_URL}/rest/v1/rpc/{rpc_name}", headers=headers, json={"query": sql})
        print(f"Trying {rpc_name}: {res.status_code} - {res.text}")
        
    # Also just check strategies to see if service_role can read it
    res_str = requests.get(f"{SUPABASE_URL}/rest/v1/strategies?select=*", headers=headers)
    print("Service role read strategies:", len(res_str.json()), "rows")

if __name__ == "__main__":
    test_rpc()
