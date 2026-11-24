from langchain_core.tools import tool
from src.search import search_documents


@tool
def search_knowledge_base(query: str) -> str:
    """
    Search the local knowledge base for information relevant
    to the user's question.

    Use this tool when the answer requires information
    from uploaded documents.
    """
    # search_documents returns List[Tuple[Document, float]]
    pairs = search_documents(query)

    if not pairs:
        return "No relevant information was found in the knowledge base."

    # Optional: drop weak matches. Chroma's default distance is
    # L2 (lower = closer). ~1.2+ is usually noise in this setup.
    MAX_DISTANCE = 1.1

    results = []
    for doc, distance in pairs:
        if distance > MAX_DISTANCE:
            continue

        filename = doc.metadata.get("source", "Unknown source")
        results.append(
            f"Source: {filename}\n\n"
            f"Content:\n{doc.page_content}"
        )

    if not results:
        return "No relevant information was found in the knowledge base."

    return "\n\n---\n\n".join(results)