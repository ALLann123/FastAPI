#!/usr/bin/python3
from pydantic import BaseModel
from typing import List

class Lesson(BaseModel):
    title: str
    duration_minutes: int
    is_free:bool

class Tutorial(BaseModel):
    name: str
    instructor: str
    lessons: List[Lesson]  # stores multiple inputs here in a list

data={
    "name":"Learn Pydantic",
    "instructor":"Own_the_Net",
    "lessons":[
        {"title":"Basic Mode", "duration_minutes": 10, "is_free":True},
        {"title":"Networking", "duration_minutes": 30, "is_free":False},
        {"title":"Coding", "duration_minutes": 9, "is_free":True},
    ]
}

# create object
lesson_object=Tutorial(**data)

#dump display
print(lesson_object.model_dump())

"""
Pydantic>python 15_excersise.py
{'name': 'Learn Pydantic', 'instructor': 'Own_the_Net', 'lessons': [{'title': 'Basic Mode', 'duration_minutes': 10, 'is_free': True}, {'title': 'Networking', 'duration_minutes': 30, 'is_free': False}, {'title': 'Coding', 'duration_minutes': 9, 'is_free': True}]}
"""