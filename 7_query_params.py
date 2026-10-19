#!/usr/bin/python3
from fastapi import FastAPI
import uvicorn

app=FastAPI()

@app.get("/hello")
async def hello(name:str, age:int):
    return {"name":name, "age":age}

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("7_query_params:app", host="127.0.0.1", port=8000, reload=True)