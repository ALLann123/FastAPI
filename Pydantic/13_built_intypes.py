#!/usr/bin/python3
from pydantic import BaseModel, EmailStr, HttpUrl, PositiveInt


class Contact(BaseModel):
    email:EmailStr
    website:HttpUrl
    followers:PositiveInt  #only numbers>0

good=Contact(
    email="hi@gmail.com",
    website="https://example.com",
    followers=992
)


print(good)
print(good.model_dump())

"""
Pydantic>python 13_built_intypes.py
email='hi@gmail.com' website=HttpUrl('https://example.com/') followers=992
{'email': 'hi@gmail.com', 'website': HttpUrl('https://example.com/'), 'followers': 992}
"""