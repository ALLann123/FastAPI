#!/usr/bin/python3
from typing import Tuple
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app=FastAPI()

class supplier(BaseModel):
    supplierID:int
    supplierName:str

class product(BaseModel):
    productID:int
    prodname:str
    price:int
    supp:supplier

class customer(BaseModel):
    custID:int
    custname:str
    prod:Tuple[product]


@app.post('/invoice')
async def getInvoice(c1:customer):
    return c1

# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("20_nested_model:app", host="127.0.0.1", port=8000, reload=True)
