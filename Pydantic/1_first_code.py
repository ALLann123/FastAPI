#!/usr/bin/python3
from pydantic import BaseModel  #enforced type hints at run time

class User(BaseModel):
    name:str  #hints required
    age:int
    is_active:bool

# create an object
user1=User(name="Jof", age=27, is_active=True)
print(user1)
print(user1.model_dump())

"""
Pydantic>python 1_first_code.py
name='Jof' age=27 is_active=True
{'name': 'Jof', 'age': 27, 'is_active': True}
"""