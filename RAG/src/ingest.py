import time
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from pypdf import PdfReader

from src.embeddings import EmbeddingGemma


DOCUMENT_DIR = Path("data/documents")
DB_DIR = "./chroma_db"
BATCH_SIZE = 32


def load_pdf(file_path: Path) -> list[Document]:
    """One Document per page, same shape PyPDFLoader produced."""
    reader = PdfReader(str(file_path))
    return [
        Document(
            page_content=page.extract_text() or "",
            metadata={"source": file_path.name, "page": index},
        )
        for index, page in enumerate(reader.pages)
    ]


def load_text(file_path: Path) -> list[Document]:
    return [
        Document(
            page_content=file_path.read_text(encoding="utf-8"),
            metadata={"source": file_path.name},
        )
    ]


def load_documents() -> list[Document]:
    documents = []
    for file_path in sorted(DOCUMENT_DIR.iterdir()):
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            documents.extend(load_pdf(file_path))
        elif suffix in (".txt", ".md"):
            documents.extend(load_text(file_path))

    # Drop empty pages (e.g. scanned PDFs with no text layer)
    return [doc for doc in documents if doc.page_content.strip()]


def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
    )
    return splitter.split_documents(documents)


def create_vector_store(chunks):
    embeddings = EmbeddingGemma()

    vector_store = Chroma(
        collection_name="knowledge_base",
        embedding_function=embeddings,
        persist_directory=DB_DIR,
    )

    ids = [
        str(
            uuid5(
                NAMESPACE_URL,
                f"{doc.metadata.get('source', '')}-"
                f"{doc.metadata.get('page', '')}-"
                f"{doc.page_content}",
            )
        )
        for doc in chunks
    ]

    # Batched so progress is visible and one failure doesn't lose everything
    for start in range(0, len(chunks), BATCH_SIZE):
        end = start + BATCH_SIZE
        vector_store.add_documents(documents=chunks[start:end], ids=ids[start:end])
        print(f"  embedded {min(end, len(chunks))}/{len(chunks)}")

    return vector_store


if __name__ == "__main__":
    start = time.perf_counter()

    print("[1] Loading documents...")
    documents = load_documents()
    print("Loaded documents:", len(documents))

    print("[2] Splitting documents...")
    chunks = split_documents(documents)
    print("Generated chunks:", len(chunks))

    print("[3] Creating vector database...")
    vector_store = create_vector_store(chunks)
    elapsed = time.perf_counter() - start

    print("[SUCCESS] Ingestion completed!")
    print("Stored chunks:", vector_store._collection.count())
    print(f"\nElapsed time: {elapsed:.2f} seconds")


"""
RAG>python -m src.ingest
[1] Loading documents...
Loaded documents: 15
[2] Splitting documents...
Generated chunks: 40
[3] Creating vector database...
[EMBEDDINGS] Connecting to ollama EmbeddingGemma-300M...
[EMBEDDINGS]Model connected successfully.
  embedded 32/40
  embedded 40/40
[SUCCESS] Ingestion completed!
Stored chunks: 45

Elapsed time: 178.65 seconds
"""