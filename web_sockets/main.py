#!/usr/bin/python3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import WebSocket
import uvicorn

templates=Jinja2Templates(directory="templates")

app=FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request:Request):
    return templates.TemplateResponse(
        request=request,
        name="socket.html"
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket:WebSocket):
    await websocket.accept()
    while True:
        data=await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)