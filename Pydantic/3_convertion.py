#!/usr/bin/python3
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    status: bool

user1=User(name="Alley", age="23", status=False)

print(user1.model_dump())

"""
>python 3_convertion.py
{'name': 'Alley', 'age': 23, 'status': False}

"""