import asyncio
from dotenv import load_dotenv
import cognee

load_dotenv()

DATASET = "axis_test_e146370b"

async def main():
    results = await cognee.recall(
        "Explain Wyckoff accumulation.",
        datasets=[DATASET],
        top_k=3,
    )
    print(results)

if __name__ == "__main__":
    asyncio.run(main())