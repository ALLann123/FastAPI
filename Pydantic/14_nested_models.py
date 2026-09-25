#!/usr/bin/python3
from pydantic import BaseModel

class Address(BaseModel):
    street:str
    city:str
    postcode:str

class User(BaseModel):
    name: str
    email:str
    address:Address


data={
    "name":"Boby",
    "email":"bob@gmail.com",
    "address":{
        "street":"123 UCL Road",
        "city":"London",
        "postcode":"AB1 2CD"
    }
}

user=User(**data)
print(user.address.city)

"""
Pydantic>python 14_nested_models.py
London
"""