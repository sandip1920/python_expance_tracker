from sqlalchemy import Column, String, Float
from database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(String, primary_key=True, index=True)
    date = Column(String)
    category = Column(String)
    amount = Column(Float)
    description = Column(String)