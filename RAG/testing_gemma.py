import ollama
import time

start=time.perf_counter()

response=ollama.embed(
    model="embeddinggemma:300m",
    input="API security involves authentication and authorization"
)

elapsed=time.perf_counter() - start

vector=response["embeddings"][0]
print("Embedding dimensions: ", len(vector))
print("First 10 values: ", vector[:10])
print(f"Elapsed time: {elapsed:.4f} seconds ({elapsed * 1000:.2f} ms)")

"""
RAG>python testing_gemma.py
Embedding dimensions:  768
First 10 values:  [-0.11794869, 0.007180422, 0.048815653, 0.044302627, 0.026721071, 0.049336977, -0.061645884, 0.008468429, 0.07893722, 0.036434002]
Elapsed time: 0.4425 seconds (442.54 ms)

"""