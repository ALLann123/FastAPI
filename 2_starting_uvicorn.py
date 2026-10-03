#!/usr/bin/python3
import uvicorn
from fastapi import FastAPI

# object creation
app=FastAPI()

# when the root directory is accessed we return the JSON(dict)
@app.get("/")
async def index():
    return {"message":"Hello World"}

if __name__=="__main__":
    #start our server
    uvicorn.run("2_starting_uvicorn:app", host="127.0.0.1", port=8000, reload=True)