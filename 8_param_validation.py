#!/usr/bin/python3
from fastapi import FastAPI, Path
import uvicorn

app=FastAPI()

@app.get("/hello/{name}")
async def hello(name:str=Path(..., min_length=3, max_length=10)):
    return {"name":name}

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("8_param_validation:app", host="127.0.0.1", port=8000, reload=True)