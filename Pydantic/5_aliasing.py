#!/usr/bin/python3
from pydantic import BaseModel, Field

class Package(BaseModel):
    weight: int=Field(alias="pkg_weight_kg")
    destination: str=Field(alias="pkg_dest")
    is_Fragile: bool=Field(alias="pkg_is_fragile")

# Order of data doesn't matter
data={
    "pkg_weight_kg":45,
    "pkg_is_fragile": True,
    "pkg_dest":"Singapore"
}

# Unpacking the dictionary
package=Package(**data) 

# we can access using own field names
print(package.weight)
print(package.destination)
print(package.is_Fragile)

#original alias names
print(package.model_dump(by_alias=True))

"""
Pydantic>python 5_aliasing.py
45
Singapore
True
{'pkg_weight_kg': 45, 'pkg_dest': 'Singapore', 'pkg_is_fragile': True}

"""