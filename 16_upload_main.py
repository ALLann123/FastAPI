#!/usr/bin/python3
from fastapi import FastAPI, UploadFile, Request, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import shutil

app=FastAPI()

templates=Jinja2Templates(directory="templates")

@app.get("/upload", response_class=HTMLResponse)
async def upload(request:Request):
    return templates.TemplateResponse(request,name="upload.html", context={"request":request})

# responsible for writing our file uploaded to the server disk
@app.post("/uploader/")
async def create_upload_file(file: UploadFile=File(...)):
    with open("destination.png", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename":file.filename}

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("16_upload_main:app", host="127.0.0.1", port=8000, reload=True)