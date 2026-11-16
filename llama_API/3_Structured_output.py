#!/usr/bin/python3
from langchain_ollama import ChatOllama
from pydantic import BaseModel

class ServerInfo(BaseModel):
    software:str
    version:str
    operating_system:str

llm=ChatOllama(
    model="qwen2.5:3b-instruct",
    temperature=0
)

structured_llm=llm.with_structured_output(ServerInfo)

result = structured_llm.invoke(
    "Apache 2.4.50 is running on Ubuntu."
)

print(result)

"""
$ python 3_structured_json.py
software='Apache' version='2.4.50' operating_system='Ubuntu'
"""