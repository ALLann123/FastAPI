#!/usr/bin/python3
import uvicorn
from fastapi import FastAPI

app=FastAPI()

@app.get("/hello/{name}/{age}")
async def hello(name:str, age:int):
    return {"name":name, "age":age}

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("6_type_vars:app", host="127.0.0.1", port=8000, reload=True)