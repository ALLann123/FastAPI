#!/usr/bin/python3
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOllama(
    model="qwen2.5:3b-instruct",
    temperature=0
)

prompt = ChatPromptTemplate.from_template("""
Classify the following message into exactly one category:

- question
- bug
- request
- other

Message:
{message}
""")

chain = prompt | llm

response = chain.invoke({
    "message": "I need assistance with my account reset?"
})

print("AI:", response.content)

"""
$ python 4_classifier.py
AI: request
"""