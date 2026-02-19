from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import csv
import os
from datetime import datetime
import uuid

FILENAME = "expenses.csv"

# Ensure CSV exists
def initialize_file():
    if not os.path.exists(FILENAME):
        with open(FILENAME, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "Date", "Category", "Amount", "Description"])

initialize_file()

# Define request body using Pydantic
class Expense(BaseModel):
    category: str
    amount: float
    description: str

class UpdateExpense(BaseModel):
    id: str
    date: str
    category: str
    amount: float
    description: str


class DeleteExpense(BaseModel):
    id: str  # Delete by unique ID


app = FastAPI(title="Personal Expense Tracker API")

# Utility: Read all expenses
def read_expenses():
    expenses = []
    with open(FILENAME, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            expenses.append(row)
    return expenses

# Utility: Write new expense
def write_expense(expense: Expense):
    expense_id = str(uuid.uuid4())  # generate unique ID
    with open(FILENAME, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            expense_id,
            datetime.now().strftime("%Y-%m-%d"),
            expense.category,
            expense.amount,
            expense.description
        ])
    return expense_id

# 1. Add Expense
@app.post("/expenses")
def add_expense(date: str, category: str, amount: float, description: str):
    expense_id = str(uuid.uuid4())  # unique ID
    with open(FILENAME, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["ID", "Date", "Category", "Amount", "Description"])
        writer.writerow({
            "ID": expense_id,
            "Date": date,
            "Category": category,
            "Amount": amount,
            "Description": description
        })
    return {"message": "Expense added successfully", "id": expense_id}

# 2. View All Expenses
@app.get("/expenses")
def get_expenses():
    return read_expenses()

# 3. Search Expenses by Category
@app.get("/expenses/category/{category}")
def get_expenses_by_category(category: str):
    expenses = [exp for exp in read_expenses() if exp["Category"].lower() == category.lower()]
    if not expenses:
        raise HTTPException(status_code=404, detail="No expenses found in this category")
    return expenses

# 4. Monthly Summary
@app.get("/expenses/summary/{month}")
def monthly_summary(month: str):  # format: YYYY-MM
    expenses = [exp for exp in read_expenses() if exp["Date"].startswith(month)]
    total = sum(float(exp["Amount"]) for exp in expenses)
    return {"month": month, "total": total, "expenses": expenses}

# 5. Highest & Lowest Expense
@app.get("/expenses/stats")
def highest_lowest_expense():
    expenses = read_expenses()
    if not expenses:
        raise HTTPException(status_code=404, detail="No expenses recorded")
    highest = max(expenses, key=lambda x: float(x["Amount"]))
    lowest = min(expenses, key=lambda x: float(x["Amount"]))
    return {"highest": highest, "lowest": lowest}

# 6. Update Expense by ID
@app.put("/expenses")
def update_expense(expense: UpdateExpense):
    try:
        # Validate date
        exp_date = datetime.strptime(expense.date, "%Y-%m-%d").strftime("%Y-%m-%d")

        expenses = read_expenses()  # list of dicts
        found = False

        for row in expenses:
            if row["ID"] == expense.id:
                row["Date"] = exp_date
                row["Category"] = expense.category.strip()
                row["Amount"] = str(expense.amount)
                row["Description"] = expense.description.strip()
                found = True
                break  # IDs are unique

        if not found:
            raise HTTPException(status_code=404, detail="Expense not found")

        # Write updated list back to CSV
        with open(FILENAME, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=["ID", "Date", "Category", "Amount", "Description"])
            writer.writeheader()
            writer.writerows(expenses)

        return {"message": "Expense updated successfully"}

    except Exception as e:
      raise HTTPException(status_code=500, detail=f"Server error: {e}")


# 7. Delete Expense by ID
@app.delete("/expenses")
def delete_expense(expense: DeleteExpense):
    expenses = read_expenses()
    updated = []
    found = False

    for row in expenses:
        if row.get("ID") == expense.id:
            found = True
            continue  # skip this row (delete)
        updated.append(row)

    if not found:
        raise HTTPException(status_code=404, detail="Expense not found")

    # Write updated CSV
    with open(FILENAME, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["ID", "Date", "Category", "Amount", "Description"])
        writer.writeheader()
        writer.writerows(updated)

    return {"message": "Expense deleted successfully"}

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the Personal Expense Tracker API. Visit /docs for API documentation."}
