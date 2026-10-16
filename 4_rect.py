#!/usr/bin/python3

class rectangle:
    def __init__(self, w:int, l:int)->None:
        self.width=w
        self.length=l

# function parameters is an object of class Rectangle with attributes width and length
def area(r:rectangle)->int:
    return r.width * r.length

# create an object
r1=rectangle(10,20)

# pass it to the area to compute area
print("area= ", area(r1))

"""
FastAPI>python 4_rect.py
area=  200

"""