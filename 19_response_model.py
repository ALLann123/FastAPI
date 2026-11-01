#!/usr/bin/python3
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, Field
import uvicorn

app=FastAPI()

class student(BaseModel):
    id: int
    name: str=Field(None, title="name of student", max_length=10)
    marks:List[int]=[]
    percent_marks:float


class percent(BaseModel):
    id:int
    name:str=Field(None, title="name of student", max_length=10)
    percent_marks:float

@app.post("/marks", response_model=percent)
async def get_percent(s1:student):
    s1.percent_marks=sum(s1.marks)/2
    return s1

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("19_response_model:app", host="127.0.0.1", port=8000, reload=True)
