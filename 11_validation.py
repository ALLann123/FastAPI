#!/usr/bin/python3
from fastapi import FastAPI, Body
from typing import List
from pydantic import BaseModel, Field
import uvicorn

app=FastAPI()

# Create our validation
class Student(BaseModel):
    id:int
    name:str=Field(None, title="name of student", max_length=10)
    subjects:List[str]=[]

# our post request when form is submited
@app.post("/students/")
async def student_data(name:str=Body(...), marks:int=Body(...)):
    return {"name":name, "marks":marks}

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("11_validation:app", host="127.0.0.1", port=8000, reload=True)
