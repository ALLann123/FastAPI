#!/usr/bin/python3
from pydantic import BaseModel, Field

class Book(BaseModel):
    title: str=Field(min_length=1, max_length=100)
    author: str
    isbn: str = Field(default=None)
    price: float=Field(gt=0, le=1000) # le stands for "less than or equal"
    in_stock:bool=Field(default=True)

# test
myBook=Book(title="Linux for Hackers", author="OTW", price=490)

# Display
print(myBook)
print(myBook.model_dump())

"""
Pydantic>python 9_exercise_1.py
title='Linux for Hackers' author='OTW' isbn=None price=490.0 in_stock=True
{'title': 'Linux for Hackers', 'author': 'OTW', 'isbn': None, 'price': 490.0, 'in_stock': True}

"""