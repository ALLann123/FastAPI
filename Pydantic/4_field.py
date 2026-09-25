#!/usr/bin/python3
from pydantic import BaseModel, Field

# Field is like a DocString and can be usefull for an LLM
class FieldUser(BaseModel):
    name: str=Field(description="The user's full name", default="John")

user1=FieldUser()
print(user1.model_dump())

"""
python 4_field.py
{'name': 'John'}

"""