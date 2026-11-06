#!/usr/bin/python3
from fastapi import FastAPI
import uvicorn

app=FastAPI()

@app.get("/app")
def mainindex():
    return {"messages":"Hello World from Top level app"}

#another app
subapp=FastAPI()
@subapp.get("/sub")
def subindex():
    return {"message":"Hello World from subapp"}

#mount the app
app.mount("/subapp", subapp)

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("24_nested_app:app", host="127.0.0.1", port=8000, reload=True)
