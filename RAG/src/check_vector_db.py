from collections import Counter
from src.search import get_vector_store

data = get_vector_store()._collection.get(include=["metadatas"])
counts = Counter((m or {}).get("source", "Unknown") for m in data["metadatas"])
for src, n in counts.most_common():
    print(f"{n:>3}  {src}")

"""
RAG>python -m src.check_vector_db
[EMBEDDINGS] Connecting to ollama EmbeddingGemma-300M...
[EMBEDDINGS]Model connected successfully.
 20  Wireless_Pwn.pdf
 16  Reccon.txt
  4  rag_notes.md
"""