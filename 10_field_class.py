#!/usr/bin/python3
from typing import List
from pydantic import BaseModel, Field

class Student(BaseModel):
    id:int
    name:str=Field(None, title="The Description of the item", max_length=10)
    subjects:List[str]=[]

data={
    "id":123,
    "name":"Walker Walker",
    "subjects":["Eng","Math","Scie"]
}

s1=Student(**data)

print(s1.model_dump())

"""
pydantic_core._pydantic_core.ValidationError: 1 validation error for Student
name
  String should have at most 10 characters
"""