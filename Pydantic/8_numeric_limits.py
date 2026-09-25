#!/usr/bin/python3
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str=Field(min_length=1, max_length=50)
    price: float=Field(gt=0) #gt stands for greater than
    description:str | None=Field(default=None, max_length=300)

# usage
valid_product=Product(name="laptop", price=99.99, description="Core i7, GPU Intel, RAM 16GB")

print(valid_product)
print(valid_product.model_dump())

"""
Pydantic>python 8_numeric_limits.py
name='laptop' price=99.99 description='Core i7, GPU Intel, RAM 16GB'
{'name': 'laptop', 'price': 99.99, 'description': 'Core i7, GPU Intel,

========Try to input the wrong thing=========
price
  Input should be greater than 0 [type=greater_than, input_value=-99.99, input_type=float]
    For further information visit https://errors.pydantic.dev/2.13/v/greater_than
"""