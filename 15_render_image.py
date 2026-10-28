#!/usr/bin/python3
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn

app=FastAPI()

templates=Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/hello/{name}", response_class=HTMLResponse)
async def hello(request:Request, name:str):
    return templates.TemplateResponse(request,"hello.html", {"name":name})


@app.get("/login/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse(request, "login.html")


# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("15_render_image:app", host="127.0.0.1", port=8000, reload=True)