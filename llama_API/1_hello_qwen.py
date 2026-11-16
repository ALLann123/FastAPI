#!/usr/bin/python3
from langchain_ollama import ChatOllama

# create connecion to our local ollama model
llm=ChatOllama(
    model="qwen2.5:3b-instruct",
    temperature=0,
    base_url="http://192.168.1.101:8000",   # <-- the Ollama daemon, not your FastAPI
)

# send a question
response=llm.invoke(
    "Explain what is an API to a begginer"
)

# display
print(response.content)
