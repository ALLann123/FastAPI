#!/usr/bin/python3
from fastapi import FastAPI, Body
from typing import List
from pydantic import BaseModel, Field
import uvicorn

app=FastAPI()

class Student(BaseModel):
    id:int
    name:str=Field(
        None,
        title="name of student",
        max_length=10,
        min_length=4 
    )
    subjects:List[str]=[]

@app.post("/students/{college}")
async def student_data(college:str, age:int, student:Student):
    retval={"college":college, "age":age, **student.model_dump()}
    return retval

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("12_request_body:app", host="127.0.0.1", port=8000, reload=True)
