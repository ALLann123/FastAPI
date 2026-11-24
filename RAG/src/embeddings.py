from langchain_ollama import OllamaEmbeddings

class EmbeddingGemma:
    def __init__(self):
        print("[EMBEDDINGS] Connecting to ollama EmbeddingGemma-300M...")

        self.model=OllamaEmbeddings(
            model="embeddinggemma:300m"
        )
        print("[EMBEDDINGS]Model connected successfully.")

    def embed_documents(self, texts:list[str])->list[list[float]]:
        """
        Convert document chunks into vector
        """
        vectors=self.model.embed_documents(texts)

        return vectors

    def embed_query(self, text: str)->list[float]:
        """
        Convert a user query into a vector
        """
        vector=self.model.embed_query(text)

        return vector

if __name__=="__main__":
    embeddings=EmbeddingGemma()
    document="API security involces authentication and authorization"
    query="How can I protect an API?"

    doc_vector=embeddings.embed_documents([document])
    query_vector=embeddings.embed_query(query)

    print("\nDocument dimesions: ", len(doc_vector[0]))
    print("Query dimensions: ", len(query_vector))

    print("\nDocument vector: ", doc_vector[0][:10])
    print("Query vector: ", query_vector[:10])

"""
RAG>python -m src.embeddings
[EMBEDDINGS] Connecting to ollama EmbeddingGemma-300M...
[EMBEDDINGS]Model connected successfully.

Document dimesions:  768
Query dimensions:  768

Document vector:  [-0.1217149, 0.013137234, 0.043867063, 0.04551638, 0.031381022, 0.045020673, -0.06517143, 0.010180093, 0.080464475, 0.03312111]
Query vector:  [-0.11149091, 0.0180716, 0.06854568, 0.008637141, 0.04589185, 0.08435198, -0.06794563, 0.032786746, 0.053848382, 0.040252168]
"""
