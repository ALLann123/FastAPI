#!/usr/bin/python3
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_ollama import ChatOllama
import uvicorn

# create the appp
app=FastAPI()

# connect langchain to our local model
llm = ChatOllama(
    model="qwen2.5:3b-instruct",
    temperature=0
)

# Generate function that streams the model response
def generate_response(message: str):
    """Pass user input to the llm"""
    for chunk in llm.stream(message):
        # Send each piece of text as soon as it is generated
        yield chunk.content

# test endpoint
@app.get("/")
def home():
    return{
        "message":"FastAPI+OLLAMA+QWEN streaming API"
    }

# streaming chat
@app.get("/chat")
def chat(message: str):
    return StreamingResponse(
        generate_response(message),
        media_type="text/plain"
    )

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
