import asyncio
import cognee

DATASET = "axis_smoke"

async def main():
    result = await cognee.remember(
        [
            r"data\knowledge\trap_mechanism.txt",
            r"data\knowledge\wyckoff.txt",
            r"data\knowledge\vsa.txt",
        ],
        dataset_name=DATASET,
        self_improvement=False,
        run_in_background=False,
    )

    print("Ingest result:")
    print(result)

    answers = await cognee.recall(
        "What is a market trap and how is it related to Wyckoff?",
        datasets=[DATASET],
        top_k=5,
        include_references=True,
    )

    print("\nRecall results:")
    for i, item in enumerate(answers, 1):
        print(f"\nResult {i}:")
        print(item)

if __name__ == "__main__":
    asyncio.run(main())