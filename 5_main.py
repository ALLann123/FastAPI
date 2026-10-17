#!/usr/bin/python3
from fastapi import FastAPI
import uvicorn

#------The last route can be a variable--------

#create an object
app=FastAPI()

# our first path
@app.get("/")
async def index():
    return {"message":"Hello World"}

# Now the route with a variable
# store input to a varible
@app.get("/hello/{name}")
async def sayHello(name):
    # show user name
    return {"name":name}


# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("5_main:app", host="127.0.0.1", port=8000, reload=True)