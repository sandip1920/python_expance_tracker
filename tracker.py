from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
import csv, os, uuid
from datetime import datetime

FILENAME = "expenses.csv"

# init file
if not os.path.exists(FILENAME):
    with open(FILENAME, "w", newline="") as f:
        csv.writer(f).writerow(["id", "date", "category", "amount", "description"])

app = FastAPI(title="Personal Expense Tracker API")

# models
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

# utils
def read_expenses():
    with open(FILENAME, "r") as f:
        return list(csv.DictReader(f))

def write_all(expenses):
    with open(FILENAME, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "date", "category", "amount", "description"])
        writer.writeheader()
        writer.writerows(expenses)

def safe_float(v):
    try:
        return float(v)
    except:
        return 0.0

# routes

# add
@app.post("/expenses")
def add_expense(expense: Expense):
    eid = str(uuid.uuid4())

    with open(FILENAME, "a", newline="") as f:
        csv.writer(f).writerow([
            eid,
            expense.date,
            expense.category,
            expense.amount,
            expense.description
        ])

    return {"message": "added", "id": eid}

# get all (filter + pagination)
@app.get("/expenses")
def get_expenses(
    category: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    data = read_expenses()

    # category filter
    if category:
        category = category.lower().strip()
        if category != "all":
            data = [e for e in data if e["category"].lower() == category]

    # amount filters
    if min_amount is not None:
        data = [e for e in data if safe_float(e["amount"]) >= min_amount]

    if max_amount is not None:
        data = [e for e in data if safe_float(e["amount"]) <= max_amount]

    return data[offset: offset + limit]

# get by id
@app.get("/expenses/{id}")
def get_one(id: str):
    for e in read_expenses():
        if e["id"] == id:
            return e
    raise HTTPException(404, "not found")

# stats
@app.get("/expenses/stats")
def stats():
    data = read_expenses()

    if not data:
        raise HTTPException(404, "no data")

    highest = max(data, key=lambda x: safe_float(x["amount"]))
    lowest = min(data, key=lambda x: safe_float(x["amount"]))
    average = sum(safe_float(e["amount"]) for e in data) / len(data)
    total = sum(safe_float(e["amount"]) for e in data)

    return {
        "highest": highest,
        "lowest": lowest,
        "average": average,
        "total": total,
        "count": len(data)
    }

# monthly summary
@app.get("/expenses/summary/{month}")
def monthly_summary(month: str):
    try:
        datetime.strptime(month, "%Y-%m")
    except:
        raise HTTPException(400, "invalid format YYYY-MM")

    data = read_expenses()
    filtered = [e for e in data if e["date"].startswith(month)]
    total = sum(safe_float(e["amount"]) for e in filtered)

    return {"month": month, "total": total, "expenses": filtered}


# update
@app.put("/expenses/{id}")
def update_expense(id: str, expense: UpdateExpense):
    data = read_expenses()
    found = False

    for e in data:
        if e["id"] == id:
            e["date"] = expense.date
            e["category"] = expense.category
            e["amount"] = str(expense.amount)
            e["description"] = expense.description
            found = True
            break

    if not found:
        raise HTTPException(404, "not found")

    write_all(data)
    return {"message": "Expense updated with id " + id}

@app.get("/dashboard")
def dashboard():
    data = read_expenses()

    if not data:
        return {"message": "no data"}

    total = sum(safe_float(e["amount"]) for e in data)
    count = len(data)
    avg = total / count

    highest = max(data, key=lambda x: safe_float(x["amount"]))
    lowest = min(data, key=lambda x: safe_float(x["amount"]))

    # category breakdown
    categories = {}
    for e in data:
        cat = e["category"]
        categories[cat] = categories.get(cat, 0) + safe_float(e["amount"])

    return {
        "total": total,
        "count": count,
        "average": avg,
        "highest": highest,
        "lowest": lowest,
        "category_breakdown": categories
    }

# delete
@app.delete("/expenses/{id}")
def delete_expense(id: str):
    data = read_expenses()
    new_data = [e for e in data if e["id"] != id]

    if len(new_data) == len(data):
        raise HTTPException(404, "not found")

    write_all(new_data)
    return {"message": "Expense deleted with id " + id}

# root
@app.get("/")
def root():
    return {"message": "Expense Tracker API"}