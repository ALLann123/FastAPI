#!/usr/bin/python3
from fastapi import FastAPI

# create an object
app=FastAPI()

#our first endpoint
@app.get("/")
async def index():
    return {"message":"Hello World"}