#!/usr/bin/python3
from pydantic import BaseModel, ConfigDict

# Base Schema with common  attributes
class ItemBase(BaseModel):
    name: str
    description: str | None=None

# schema for creating a new item
class ItemCreate(ItemBase):
    pass

# Schema for reading/returning an item(includes id)
class Item(ItemBase):
    id:int

    model_config=ConfigDict(from_attributes=True)
