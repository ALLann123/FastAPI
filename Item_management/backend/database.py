#!/usr/bin/python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Database URL for sqlite(create a file test.db)
SQLALCHEMY_DATABASE_URL= "sqlite:///./test.db"

# create the database engine
engine=create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread":False}
)

# create a SessionLocal class for database sessions
SessionLocal=sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create a BAse class for our models
class Base(DeclarativeBase):
    pass


