import asyncio
from src.scheduling.token_refresher import refresh_if_needed
try:
    asyncio.run(asyncio.wait_for(refresh_if_needed(), timeout=5.0))
    print("Success")
except Exception as e:
    print(f"Exception: {e}")
