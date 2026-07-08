import os
import glob
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

def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 300) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            # Try to break at a double newline first (paragraph)
            next_break = text.rfind('\n\n', start, end)
            if next_break == -1:
                next_break = text.rfind('\n', start, end)
            if next_break == -1:
                next_break = text.rfind(' ', start, end)
            if next_break > start + (chunk_size // 2):
                end = next_break
        chunks.append(text[start:end].strip())
        start = end - overlap
        if start <= end - chunk_size:
            start = end # fallback if overlap logic fails
    return [c for c in chunks if c]

def ingest_knowledge():
    client = get_supabase_client()
    knowledge_files = glob.glob(r"data\knowledge\*.txt")
    
    if not knowledge_files:
        print("No knowledge files found.")
        return

    print("Clearing old knowledge chunks...")
    client.table("knowledge_chunks").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

    for file_path in knowledge_files:
        filename = os.path.basename(file_path)
        print(f"Ingesting {filename}...")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        chunks = chunk_text(content)
        for i, chunk in enumerate(chunks):
            if not chunk:
                continue
            
            vec = get_gemini_embedding(chunk)
            
            client.table("knowledge_chunks").insert({
                "content": chunk,
                "embedding": vec,
                "source_file": filename,
                "chunk_index": i
            }).execute()
            
    print("Ingestion completed successfully!")

if __name__ == "__main__":
    ingest_knowledge()
