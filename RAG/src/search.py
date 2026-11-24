from langchain_chroma import Chroma
from src.embeddings import EmbeddingGemma

def get_vector_store():
    embeddings=EmbeddingGemma()

    return Chroma(
        collection_name="knowledge_base",
        embedding_function=embeddings,
        persist_directory="./chroma_db"
    )

def search_documents(query: str, k:int=4):
    vector_store=get_vector_store()

    result=vector_store.similarity_search_with_score(
        query,
        k=k
    )
    return result

if __name__=="__main__":

    while True:
        query=input("Ask your knowledge base: ")

        if query in ["exit", "quit"]:
            break

        if query =="":
            continue

        results = search_documents(query)

        for document, distance in results:

            print("\n--------------------------")

            print("Source:", document.metadata.get("source"))

            print("Content:", document.page_content)

            print("Distance:", distance)

        print("\n\n")
"""
RAG>python -m src.search
Ask your knowledge base: What is RAG
[EMBEDDINGS] Connecting to ollama EmbeddingGemma-300M...
[EMBEDDINGS]Model connected successfully.

--------------------------
Source: rag_notes.md
Content: # RAG (Retrieval-Augmented Generation)

RAG is a technique that combines **information retrieval** with **language generation**. Instead of relying solely on an LLM's parametric memory, RAG retrieves relevant documents from an external knowledge base and feeds them into the prompt as context.

## Why RAG?

- **Freshness** — knowledge stays current without retraining
- **Grounding** — answers cite real sources, reducing hallucination
- **Privacy** — private data stays in your own store
- **Cost** — cheaper than fine-tuning for factual recall
- **Traceability** — you can show _where_ an answer came from

## Core Pipeline

Documents → Chunk → Embed → Vector Store
↓
Query → Embed → Retrieve top-k → Prompt + Context → LLM → Answer
Distance: 0.829954206943512

--------------------------
Source: None
Content: API rate limiting helps prevent excessive requests.
Distance: 1.2406152486801147

--------------------------
Source: None
Content: React is a JavaScript library for building user interfaces.
Distance: 1.3117115497589111

--------------------------
Source: None
Content: SQL injection occurs when untrusted input is improperly handled in SQL queries.
Distance: 1.3529366254806519



Ask your knowledge base:
Ask your knowledge base:
Ask your knowledge base:
Ask your knowledge base: How does JWT authentication work?
[EMBEDDINGS] Connecting to ollama EmbeddingGemma-300M...
[EMBEDDINGS]Model connected successfully.

--------------------------
Source: None
Content: JWT is commonly used for API authentication.
Distance: 0.6656926870346069

--------------------------
Source: None
Content: SQL injection occurs when untrusted input is improperly handled in SQL queries.
Distance: 1.1933408975601196

--------------------------
Source: None
Content: API rate limiting helps prevent excessive requests.
Distance: 1.2555054426193237

--------------------------
Source: None
Content: FastAPI is a Python framework for building APIs.
Distance: 1.3302338123321533



Ask your knowledge base: What is John the ripper used for?
[EMBEDDINGS] Connecting to ollama EmbeddingGemma-300M...
[EMBEDDINGS]Model connected successfully.

"""