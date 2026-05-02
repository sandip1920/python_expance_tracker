from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
import models, schemas
from database import SessionLocal, engine
from auth.routes import router as auth_router
from auth.dependencies import get_current_user

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Expense Tracker API")

app.include_router(auth_router, prefix="/auth", tags=["Auth"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def safe_float(v):
    try:
        return float(v)
    except:
        return 0.0

# add
@app.post("/expenses")
def add_expense(expense: schemas.Expense, db: Session = Depends(get_db), user = Depends(get_current_user)):
    eid = str(uuid.uuid4())

    new_expense = models.Expense(
        id=eid,
        date=expense.date,
        category=expense.category,
        amount=expense.amount,
        description=expense.description,
        user_id=user["user_id"]
    )

    db.add(new_expense)
    db.commit()

    return {"message": "added", "id": eid}

# get all
@app.get("/expenses")
def get_expenses(
    category: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    data = db.query(models.Expense).filter(models.Expense.user_id == user["user_id"]).all()

    
    data = [e.__dict__ for e in data]
    for e in data:
        e.pop("_sa_instance_state", None)

    if category:
        category = category.lower().strip()
        if category != "all":
            data = [e for e in data if e["category"] == category]

    if min_amount is not None:
        data = [e for e in data if safe_float(e["amount"]) >= min_amount]

    if max_amount is not None:
        data = [e for e in data if safe_float(e["amount"]) <= max_amount]

    return data[offset: offset + limit]

# stats
@app.get("/expenses/stats")
def stats(db: Session = Depends(get_db), user = Depends(get_current_user)):
    data = db.query(models.Expense).filter(models.Expense.user_id == user["user_id"]).all()

    if not data:
        raise HTTPException(404, "no data")

    data = [e.__dict__ for e in data]
    for e in data:
        e.pop("_sa_instance_state", None)

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


# get by id
@app.get("/expenses/{id}")
def get_one(id: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    e = db.query(models.Expense).filter(models.Expense.id == id).first()
    if not e:
        raise HTTPException(404, "not found")

    result = e.__dict__
    result.pop("_sa_instance_state", None)
    return result


# monthly summary
@app.get("/expenses/summary/{month}")
def monthly_summary(month: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    try:
        datetime.strptime(month, "%Y-%m")
    except:
        raise HTTPException(400, "invalid format YYYY-MM")

    data = db.query(models.Expense).filter(models.Expense.user_id == user["user_id"]).all()
    data = [e.__dict__ for e in data]
    for e in data:
        e.pop("_sa_instance_state", None)

    filtered = [e for e in data if e["date"].startswith(month)]
    total = sum(safe_float(e["amount"]) for e in filtered)

    return {"month": month, "total": total, "expenses": filtered}

# update
@app.put("/expenses/{id}")
def update_expense(id: str, expense: schemas.UpdateExpense, db: Session = Depends(get_db), user = Depends(get_current_user)):
    e = db.query(models.Expense).filter(models.Expense.id == id).first()

    if not e:
        raise HTTPException(404, "not found")

    e.date = expense.date
    e.category = expense.category
    e.amount = expense.amount
    e.description = expense.description

    db.commit()

    return {"message": "Expense updated with id " + id}

# dashboard
@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user = Depends(get_current_user)):
    data = db.query(models.Expense).filter(models.Expense.user_id == user["user_id"]).all()

    if not data:
        return {"message": "no data"}

    data = [e.__dict__ for e in data]
    for e in data:
        e.pop("_sa_instance_state", None)

    total = sum(safe_float(e["amount"]) for e in data)
    count = len(data)
    avg = total / count

    highest = max(data, key=lambda x: safe_float(x["amount"]))
    lowest = min(data, key=lambda x: safe_float(x["amount"]))

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
def delete_expense(id: str, db: Session = Depends(get_db), user = Depends(get_current_user)):
    e = db.query(models.Expense).filter(models.Expense.id == id).first()

    if not e:
        raise HTTPException(404, "not found")

    db.delete(e)
    db.commit()

    return {"message": "Expense deleted with id " + id}

# root
@app.get("/")
def root():
    return {"message": "Expense Tracker API"}