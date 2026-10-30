#!/usr/bin/python3
from fastapi import FastAPI, Cookie
from fastapi.responses import JSONResponse
import uvicorn

app=FastAPI()


@app.post("/cookie/")
def create_cookie():
    content={"message":"cookie set"}
    response=JSONResponse(content=content)
    response.set_cookie(key="username", value="admin")
    return response

@app.get("/readcookie/")
async def read_cookie(username: str=Cookie(None)):
    return {"username":username}

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("17_set_cookie:app", host="127.0.0.1", port=8001, reload=True)
