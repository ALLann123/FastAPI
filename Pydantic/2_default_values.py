#!/usr/bin/python3
from pydantic import BaseModel

class Student(BaseModel):
    name: str
    age: int=18
    course: str

stud1=Student(name="Walker", course="Computer Science", age=29)
print(stud1.model_dump())

"""
python 2_default_values.py
{'name': 'Walker', 'age': 18, 'course': 'Computer Science'}

# Try over writing
python 2_default_values.py
{'name': 'Walker', 'age': 29, 'course': 'Computer Science'}

"""