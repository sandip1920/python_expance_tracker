from sqlalchemy import Column, String, Float
from app.database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String, primary_key=True, index=True)
    date = Column(String)
    category = Column(String)
    amount = Column(Float) 
    description = Column(String)
    user_id = Column(String, index=True, nullable=False) 


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)