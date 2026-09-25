#!/usr/bin/python3
from pydantic import BaseModel, model_validator

class Event(BaseModel):
    name: str
    start_hour:int
    end_hour:int

    # class method for additional checks
    @model_validator(mode='after') # use a decorator
    def check_time(self):
        if self.end_hour<=self.start_hour:
            raise ValueError("end_hour must be greater that start_hour. Fix it!!")

        return self

# will throw error
event1=Event(name="Hackathon", start_hour=9, end_hour=11)

# Display
print(event1)
print(event1.model_dump())

"""
pydantic_core._pydantic_core.ValidationError: 1 validation error for Event
  Value error, end_hour must be greater that start_hour. Fix it!! [type=value_error, input_value={'name': 'Hackathon', 'st...our': 10, 'end_hour': 9}, input_type=dict]

=====Fixed Error=======
Pydantic>python 10_validation_intro.py
name='Hackathon' start_hour=9 end_hour=11
{'name': 'Hackathon', 'start_hour': 9, 'end_hour': 11}

"""