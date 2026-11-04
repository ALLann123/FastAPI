#!/usr/bin/python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy import Column, Integer, String
from typing import List
from pydantic import BaseModel, ConfigDict
from fastapi import FastAPI, Depends
import uvicorn

# create our sql db
SQLALCHEMY_DATABASE_URL="sqlite:///./test.db"
engine=create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread":False}
)

# get the db session handle to interact with it
session=sessionmaker(autocommit=False, autoflush=False, bind=engine)

# maps our classes to tables
Base=declarative_base()

"""
Books class, a subclass of Base is mapped to a book table
in the database

create_all() --> creates the tables in the database
"""
class Books(Base):
    __tablename__='book'
    id=Column(Integer, primary_key=True, nullable=False)
    title=Column(String(50), unique=True)
    author=Column(String(50))
    publisher=Column(String(50))

#Create the table in the database
Base.metadata.create_all(bind=engine)

# pydantic model that corresponds to the declarative base subclass
class Book(BaseModel):
    id:int
    title:str
    author:str
    publisher:str

    model_config=ConfigDict(from_attributes=True)
    
app=FastAPI()

def get_db():
    db=session()
    try:
        yield db
    finally:
        db.close()

@app.post('/add_new', response_model=Book)
def add_book(b1:Book, db:Session=Depends(get_db)):
    bk=Books(
        id=b1.id,
        title=b1.title,
        author=b1.author,
        publisher=b1.publisher
    )
    db.add(bk)
    db.commit()
    db.refresh(bk)
    return bk

@app.put('/update/{id}', response_model=Book)
def update_book(id:int, book:Book, db: Session = Depends(get_db)):
   b1 = db.query(Books).filter(Books.id == id).first()
   b1.id=book.id
   b1.title=book.title
   b1.author=book.author
   b1.publisher=book.publisher
   db.commit()
   return db.query(Books).filter(Books.id == id).first()

@app.delete('/delete/{id}')
def del_book(id:int, db: Session = Depends(get_db)):
   try:
      db.query(Books).filter(Books.id == id).delete()
      db.commit()
   except Exception as e:
      raise Exception(e)
   return {"delete status": "success"}

# lists records from our db
@app.get('/list', response_model=List[Book])
def get_books(db:Session=Depends(get_db)):
    recs=db.query(Books).all()
    return recs

# returns results according to the id passed
@app.get('/book/{id}', response_model=Book)
def get_book(id:int, db:Session=Depends(get_db)):
    return db.query(Books).filter(Books.id==id).first()


# start our server
if __name__=="__main__":
    #start our server
    uvicorn.run("22_db_interact:app", host="127.0.0.1", port=8000, reload=True)
