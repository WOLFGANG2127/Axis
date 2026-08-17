import asyncio
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

from src.database.supabase import get_supabase_client
from src.scheduling.token_refresher import refresh_if_needed
from src.config.settings import settings

async def main():
    client = get_supabase_client()
    
    print("Initializing test...")
    # Seed the broker_tokens table with current DHAN_ACCESS_TOKEN if empty
    now_utc = datetime.now(timezone.utc)
    future_expiry = now_utc + timedelta(hours=24)
    
    # Try inserting/updating id=1
    try:
        client.table("broker_tokens").upsert({
            "id": 1,
            "access_token": settings.DHAN_ACCESS_TOKEN,
            "generated_at": now_utc.isoformat(),
            "expires_at": future_expiry.isoformat()
        }).execute()
        print("✅ Seeded broker_tokens with active token.")
    except Exception as e:
        print(f"❌ Failed to seed table (did you run the migration 009?): {e}")
        return

    print("\n--- Test 1: Active Token (expires in > 2 hours) ---")
    try:
        result = await refresh_if_needed()
        print(f"Result: {result}")
        assert result["action"] == "none", "Should do nothing for active token"
        print("✅ Test 1 Passed.")
    except Exception as e:
        print(f"❌ Test 1 Failed: {e}")

    print("\n--- Test 2: Expiring Token (expires in < 2 hours) ---")
    try:
        # Backdate expiry to simulate near-expiry
        past_expiry = now_utc + timedelta(hours=1)
        client.table("broker_tokens").update({"expires_at": past_expiry.isoformat()}).eq("id", 1).execute()
        
        result = await refresh_if_needed()
        print(f"Result: {result}")
        assert result["action"] in ["renew", "generate"], "Should renew or generate"
        print("✅ Test 2 Passed.")
    except Exception as e:
        print(f"❌ Test 2 Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
