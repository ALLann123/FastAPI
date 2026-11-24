import chromadb

client=chromadb.PersistentClient(
    path="./chroma_db"
)

collection=client.get_collection(
    name="knowledge_base"
)

print("Total record: ", collection.count())

results=collection.get(
    include=["documents", "metadatas"]
)

for doc_id, document, metadata in zip(
    results["ids"],
    results["documents"],
    results["metadatas"]
):
    print("\nID:", doc_id)
    print("Document:", document)
    print("Metadata:", metadata)

"""
RAG>python -m src.inspect_db
Total record:  5

ID: 6154fca8-e545-42f8-b477-70727dac3bdb
Document: FastAPI is a Python framework for building APIs.
Metadata: None

ID: e94a6df9-44f6-481f-b136-2b68cd0e3eab
Document: JWT is commonly used for API authentication.
Metadata: None

ID: f29a35fa-5a60-409e-95d8-e71201eef90c
Document: SQL injection occurs when untrusted input is improperly handled in SQL queries.
Metadata: None

ID: 70280acd-4a61-40f8-bf82-ad81dc9ec2c8
Document: React is a JavaScript library for building user interfaces.
Metadata: None

ID: 38216e76-aaa2-44ee-a5ab-53d9e01efbc9
Document: API rate limiting helps prevent excessive requests.
Metadata: None

"""