#!/usr/bin/python3
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app=FastAPI()

@app.get("/rspheader/")
def set_rsp_headers():
    content={"message":"Hello World"}
    headers={"X-Web-Framework":"FastAPI", "Content-Language":"en-US"}
    return JSONResponse(content=content, headers=headers)

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("18_headers:app", host="127.0.0.1", port=8000, reload=True)
