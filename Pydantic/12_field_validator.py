#!/usr/bin/python3
from pydantic import BaseModel, field_validator

class Product(BaseModel):
    price: float

    @field_validator("price")
    def must_be_positive(value):
        if value<=0:
            raise ValueError("Price must be greater than 0")

        return value

product1=Product(price=93)

print(product1.model_dump())

"""
Pydantic>python 12_field_validator.py
{'price': 93.0}

=====change 93 to -93=========
price
  Value error, Price must be greater than 0 [type=value_error, input_value=-93, input_type=int]
    For further information visit https://errors.pydantic.dev/2.13/v/value_error
"""