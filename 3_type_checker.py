#!/usr/bin/python3

def division(x:int, y:int)-> int:
    return (x//y)

# pass integers
a=division(10,2)
print(a)

# pass floating point
b=division(5, 2.5)
print(b)

# Pass a string
c=division("hello", 10)
print(c)