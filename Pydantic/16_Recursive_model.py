#!/usr/bin/python3
from pydantic import BaseModel
from typing import List, Optional

class FamilyTree(BaseModel):
    name: str
    children: Optional[List["FamilyTree"]]=None # use string for forward reference

FamilyTree.model_rebuild()   #tells pydantic to rebuild the model after the whole class

data={
    "name":"root",
    "children":[
    {
        "name":"child_1",
        "children":[
            {"name":"grandchild_1"},
            {"name":"grandchild_2"}
        ]
    },
    {
        "name":"child_2",
        "children":[{"name":"grandchild_3"}]
    }
    ],
}


tree=FamilyTree(**data)
print(tree.model_dump())

"""
Pydantic>python 16_Recursive_model.py
{'name': 'root', 'children': [{'name': 'child_1', 'children': [{'name': 'grandchild_1', 'children': None}, {'name': 'grandchild_2', 'children': None}]}, {'name': 'child_2', 'children': [{'name': 'grandchild_3', 'children': None}]}]}

"""