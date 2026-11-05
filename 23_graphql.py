#!/usr/bin/python3
import strawberry
from strawberry.asgi import GraphQL
from fastapi import FastAPI
import uvicorn

#decorate a python class
@strawberry.type
class Book:
    title:str
    author:str
    price:int

# Declare a Query class containing a function that returns a Book object
@strawberry.type
class Query:
    @strawberry.field
    def book(self)-> Book:
        return Book(title="Computer Fundamentals", author="Sinha", price=200)

#use the Query class to obtain strawberry.schema object
schema=strawberry.Schema(query=Query)

# declare objects of GraphQL class
graphql_app=GraphQL(schema)
app=FastAPI()

# add routes to the FastAPI object and run the server
app.add_route("/book", graphql_app)
app.add_api_websocket_route("/book", graphql_app)


# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("23_graphql:app", host="127.0.0.1", port=8000, reload=True)
