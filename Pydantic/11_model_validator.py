#!/usr/bin/python3
from pydantic import BaseModel, model_validator

class Delivery(BaseModel):
    pickup: int
    drop: int

    @model_validator(mode='before')
    @classmethod
    def fix_input(cls, data):
        print("Before validator sees raw input: ", data)

        # swap them if they are reversed
        if int(data['drop']) < int(data['pickup']):
            data['pickup'], data['drop']=data['drop'], data['pickup']
        return data

order1=Delivery(pickup=15, drop=13)
print("After model validation: ", order1.model_dump())

"""
Pydantic>python 11_model_validator.py
Before validator sees raw input:  {'pickup': 15, 'drop': 13}
After model validation:  {'pickup': 13, 'drop': 15}

"""