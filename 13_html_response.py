#!/usr/bin/python3
from fastapi import FastAPI
import uvicorn
from fastapi.responses import HTMLResponse

app=FastAPI()

@app.get("/hello/")
async def hello():
    ret='''
    <html>
    <body>
        <h2>Hello World</h2>
    </body>
    </html>
'''
    return HTMLResponse(content=ret)

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("13_html_response:app", host="127.0.0.1", port=8000, reload=True)
