#!/usr/bin/python3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn

app=FastAPI()

templates=Jinja2Templates(directory="templates")


@app.get("/hello/", response_class=HTMLResponse)
async def hello(request:Request):
    return templates.TemplateResponse(request,"hello.html")

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("14_render_html:app", host="127.0.0.1", port=8000, reload=True)
