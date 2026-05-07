from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class Expense(BaseModel):
    date: str
    category: str = Field(min_length=2, max_length=50)
    amount: float = Field(gt=0)
    description: str = Field(min_length=2, max_length=200)

    @field_validator("date")
    @classmethod
    def validate_date(cls, v):
        try:
            return datetime.strptime(v, "%Y-%m-%d").strftime("%Y-%m-%d")
        except:
            raise ValueError("Date must be YYYY-MM-DD")

    @field_validator("category", "description")
    @classmethod
    def normalize(cls, v):
        return v.strip().lower()

class UpdateExpense(Expense):
    pass

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str