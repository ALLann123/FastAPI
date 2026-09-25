#!/usr/bin/python3
from pydantic import BaseModel, Field

class Student(BaseModel):
    email: str=Field(
        validation_alias="student_email",  # Accepts this as input
        serialization_alias="studentEmail"  #Outputs this name
    )

# Incoming data
incoming_data={
    "student_email":"hi@gmail.com"
}

# create object
stud1=Student(**incoming_data)

# display
print(stud1.email)

print(stud1.model_dump())
print(stud1.model_dump(by_alias=True))

"""
Pydantic>python 6_aliasing_stud.py
hi@gmail.com
{'email': 'hi@gmail.com'}
{'studentEmail': 'hi@gmail.com'}
"""