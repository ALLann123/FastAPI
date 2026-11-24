# RAG (Retrieval-Augmented Generation)

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

1. **Ingest** — load documents (PDF, HTML, DB, etc.)
2. **Chunk** — split into passages (e.g. 200–800 tokens with overlap)
3. **Embed** — convert chunks to vectors with an embedding model
4. **Index** — store vectors (FAISS, pgvector, Qdrant, Pinecone…)
5. **Retrieve** — embed the query, find nearest neighbors (top-k)
6. **Augment** — insert retrieved chunks into the prompt
7. **Generate** — LLM answers using the provided context

## Key Design Choices

| Choice          | Options                        | Trade-off                   |
| --------------- | ------------------------------ | --------------------------- |
| Chunking        | fixed / semantic / recursive   | recall vs. precision        |
| Embedding model | open (BGE, E5) / API (OpenAI)  | cost vs. quality            |
| Retrieval       | dense / sparse (BM25) / hybrid | semantics vs. keywords      |
| Reranking       | cross-encoder rerank           | latency vs. accuracy        |
| Top-k           | 3–10 typical                   | context budget vs. coverage |

## Common Improvements

- **Hybrid search** — combine BM25 + dense vectors
- **Reranking** — re-score candidates with a cross-encoder
- **Query rewriting** — expand or decompose user queries
- **Metadata filtering** — restrict by date, source, tenant
- **Citations** — return chunk IDs so users can verify
- **Evaluation** — track retrieval recall and answer faithfulness (RAGAS, TruLens)

## Failure Modes

- **Bad chunking** — splits answers across chunks
- **Missing context** — retriever misses the right doc
- **Distractor noise** — irrelevant chunks confuse the LLM
- **Stale index** — documents not re-ingested
- **Over-trusting context** — model parrots wrong retrieved text

## Minimal Example (pseudo-code)

```python
chunks = split(load("docs/"))
index = VectorStore([embed(c) for c in chunks])

def answer(query):
    hits = index.search(embed(query), k=5)
    context = "\n\n".join(h.text for h in hits)
    prompt = f"Use the context to answer.\n\n{context}\n\nQ: {query}"
    return llm(prompt)
```
