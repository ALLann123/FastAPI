#!/usr/bin/python3
from pydantic import BaseModel, Field

class Book(BaseModel):
    title: str=Field(
        validation_alias="book_title",  # Input will use this
        serialization_alias="bookTitle" # Output will use this
    )
    author: str=Field(
        validation_alias="author_name", #input will use this
        serialization_alias="authorName" # output will use this
    )

# pass our input data in the JSOn/Dictionary
backend_data={
    "book_title":"Pydantic Guide",
    "author_name":"Own_the_Net"
}

# create an object
book=Book(**backend_data)

#display
print(book.title)
print(book.author)
print(book.model_dump())
print(book.model_dump(by_alias=True))


"""
Pydantic>python 7_book_class.py
Pydantic Guide
Own_the_Net
{'title': 'Pydantic Guide', 'author': 'Own_the_Net'}
{'bookTitle': 'Pydantic Guide', 'authorName': 'Own_the_Net'}

"""