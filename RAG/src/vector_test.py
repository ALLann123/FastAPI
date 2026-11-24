from langchain_chroma import Chroma
from src.embeddings import EmbeddingGemma
import time

start=time.perf_counter()
# load embeding model
embeddings=EmbeddingGemma()

# create persistent vector database
vector_store=Chroma(
    collection_name="knowledge_base",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)

# sample document
documents=[
    "FastAPI is a Python framework for building APIs.",

    "JWT is commonly used for API authentication.",

    "SQL injection occurs when untrusted input "
    "is improperly handled in SQL queries.",

    "React is a JavaScript library for building "
    "user interfaces.",

    "API rate limiting helps prevent excessive requests."
]

# store document
vector_store.add_texts(documents)

print("Document successfully stored!")

# Search
query="How can I prevent excessive API requests?"

results=vector_store.similarity_search(
    query,
    k=3
)

elapsed=time.perf_counter() - start
print("\nSearch results: ")


for result in results:
    print("-----------------------")
    print(result.page_content)

print(f"\n\nElapsed time: {elapsed:.4f} seconds ({elapsed * 1000:.2f} ms)")

"""
RAG>python -m src.vector_test
[EMBEDDINGS] Connecting to ollama EmbeddingGemma-300M...
[EMBEDDINGS]Model connected successfully.
Document successfully stored!

Search results:
-----------------------
API rate limiting helps prevent excessive requests.
-----------------------
JWT is commonly used for API authentication.
-----------------------
FastAPI is a Python framework for building APIs.


Elapsed time: 77.9725 seconds (77972.51 ms)
"""