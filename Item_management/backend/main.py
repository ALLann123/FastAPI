#!/usr/bin/python3
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal, engine


# Startup/shutdown logic (replaces the deprecated @app.on_event handlers)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # create all tables in the database on startup
    models.Base.metadata.create_all(bind=engine)
    yield


# create the FastAPI application
app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow React frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React's default port
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Reusable annotated dependency type
DbSession = Annotated[Session, Depends(get_db)]


# CREATE --> Add a new item
@app.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: DbSession):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# READ --> Get all items
@app.get("/items/", response_model=list[schemas.Item])
def read_items(db: DbSession, skip: int = 0, limit: int = 100):
    return db.scalars(select(models.Item).offset(skip).limit(limit)).all()


# READ --> Get a single item by ID
@app.get("/items/{item_id}", response_model=schemas.Item)
def read_item(item_id: int, db: DbSession):
    item = db.get(models.Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# UPDATE --> Update an existing item
@app.put("/items/{item_id}", response_model=schemas.Item)
def update_item(item_id: int, item: schemas.ItemCreate, db: DbSession):
    db_item = db.get(models.Item, item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    for field, value in item.model_dump().items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item


# DELETE --> Remove an item
@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: DbSession):
    item = db.get(models.Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(item)
    db.commit()
    return {"message": "Item deleted successfully"}