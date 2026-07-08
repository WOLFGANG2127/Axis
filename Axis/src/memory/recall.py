import os
from litellm import embedding
from src.database.supabase import get_supabase_client
from dotenv import load_dotenv

load_dotenv()

def get_gemini_embedding(text: str) -> list[float]:
    response = embedding(
        model="gemini/gemini-embedding-001",
        input=[text]
    )
    return response.data[0]["embedding"]

def recall_knowledge(query: str, top_k: int = 3, match_threshold: float = 0.5) -> list[dict]:
    client = get_supabase_client()
    query_vec = get_gemini_embedding(query)
    
    response = client.rpc("match_knowledge_chunks", {
        "query_embedding": query_vec,
        "match_threshold": match_threshold,
        "match_count": top_k
    }).execute()
    
    return response.data

if __name__ == "__main__":
    import sys
    query = sys.argv[1] if len(sys.argv) > 1 else "Explain Wyckoff accumulation."
    print(f"Recalling for query: {query}")
    results = recall_knowledge(query)
    for i, res in enumerate(results):
        print(f"\n--- Result {i+1} (Sim: {res['similarity']:.4f}) from {res['source_file']} ---")
        print(res['content'])
