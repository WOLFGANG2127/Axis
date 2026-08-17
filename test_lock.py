import asyncio
from src.llm.distributed_lock import acquire, release

async def main():
    print("Testing distributed lock acquisition...")
    acq1 = await acquire("test_lock", ttl_seconds=10)
    print(f"Acquired first time: {acq1}")
    
    acq2 = await acquire("test_lock", ttl_seconds=10)
    print(f"Acquired second time (same worker, should be False if we follow strict logic, but let's see): {acq2}")
    
    print("Releasing lock...")
    await release("test_lock")
    print("Released!")
    
    acq3 = await acquire("test_lock", ttl_seconds=10)
    print(f"Acquired third time (after release): {acq3}")

if __name__ == "__main__":
    asyncio.run(main())
