#!/usr/bin/python3
from typing import Literal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from pydantic import BaseModel
import uvicorn

#---Setting
MODEL_NAME="qwen2.5:3b-instruct"
SYSTEM_PROMPT=(
    "You are called Mr.Robot. A cyberSecurity assistant" \
    "Keep Answers clear and concise. Make them short as possible" \
    "Use Markdown when it helps, and put code in fenced code blocks"
)

# only send the last 20 messages to the model
MAX_HISTORY=20

#----Create the App
app=FastAPI(title="Local LLM Chat API")
# CORS: Allows the React Dev Server call this API
# without this the browser blocks the request
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://192.168.1.100:5173",
        "http://192.168.1.106:3000", #our machine IP address
        "http://192.168.1.106:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect LangChain to our local model
llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0.1,
)



# ------Request Shapes(Pydantic Validates incoming JSON for us)
class ChatMessage(BaseModel):
    role:Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage]

# Helpers
def to_langchain_messages(messages: list[ChatMessage]):
    """Turn our simple messages into LangChain message objects."""
    result=[SystemMessage(content=SYSTEM_PROMPT)]
    for m in messages[-MAX_HISTORY:]:
        if m.role=="user":
            result.append(HumanMessage(content=m.content))
        else:
            result.append(AIMessage(content=m.content))
    return result


def generate_response(prompt):
    """
    Stream the model's reply piece by piece
    `prompt` can be a plain string or a list of langchain messages.
    """
    try:
        for chunk in llm.stream(prompt):
            # Send each piece of text as soon as it is generated
            yield chunk.content

    except Exception as error:
        # By now the response has already started (status 200) so we
        # send the error as text and let the browser show it
        yield(
            f"\n\nCould not reach the model ({error})"
            "Is Ollama running? Try `ollama serve`."
        )


STREAM_HEADERS={
    "Cache-Control":"no-cache",
    "X-Accel-Buffering": "no",  # stops proxies like nginx from buffering
}

#-------------------------
#   Endpoints
#-------------------------
# test endpoint(check is the server up)
@app.get("/")
def home():
    return {
        "message":"FastAPI+OLLAMA+QWEN streaming API",
        "model":MODEL_NAME
    }

# Original streaming endpoint: One message, handy for curl tests
@app.get("/chat")
def chat_simple(message: str):
    return StreamingResponse(
        generate_response(message),
        media_type="text/plain",
        headers=STREAM_HEADERS,
    )

# Chat enpoint for React: receives the whole conversation so the
# model remembers what was said earlier
@app.post("/chat")
def chat(request: ChatRequest):
    return StreamingResponse(
        generate_response(to_langchain_messages(request.messages)),
        media_type="text/plain",
        headers=STREAM_HEADERS,
    )


# start our server
if __name__ == "__main__":
    # 0.0.0.0 = listen on every network interface, so both
    # localhost and 192.168.1.100 work
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
