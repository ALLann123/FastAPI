#!/usr/bin/python3
from pydantic import BaseModel
from typing import List

class Student(BaseModel):
    id: int
    name: str
    subjects:List[str]=[]


data={
    "id":1,
    "name":"Walker",
    "subjects":["math","C++","AI"]
}

s1=Student(**data)

print(s1)

print(s1.model_dump())

"""
FastAPI>python 9_stud_pyda.py
id=1 name='Walker' subjects=['math', 'C++', 'AI']
{'id': 1, 'name': 'Walker', 'subjects': ['math', 'C++', 'AI']}
"""
