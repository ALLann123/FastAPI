#!/usr/bin/python3
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

llm=ChatOllama(
    model="qwen2.5:3b-instruct",
    temperature=0
)

messages=[
    SystemMessage(
        content="You are a Red team specialist in penetration testing"
    ),
    HumanMessage(
        content="Burp Suite automation in 3 statements?"
    )
]

# stream
print("AI: ", end="", flush=True)
for chunk in llm.stream(messages):
    print(chunk.content, end="", flush=True)
print("\n")