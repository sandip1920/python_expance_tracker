from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import csv
import os
from datetime import datetime

FILENAME = "expenses.csv"

# Ensure CSV exists
def initialize_file():
    if not os.path.exists(FILENAME):
        with open(FILENAME, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Category", "Amount", "Description"])

initialize_file()

# Define request body using Pydantic
class Expense(BaseModel):
    category: str
    amount: float
    description: str

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
    with open(FILENAME, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime("%Y-%m-%d"),
                         expense.category, expense.amount, expense.description])

# 1. Add Expense
@app.post("/expenses")
def add_expense(expense: Expense):
    write_expense(expense)
    return {"message": "Expense added successfully"}

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

# 6. Delete an Expense (match exact row)
@app.delete("/expenses")
def delete_expense(date: str, category: str, amount: float, description: str):
    expenses = read_expenses()
    updated = [row for row in expenses if not (
        row["Date"] == date and
        row["Category"] == category and
        float(row["Amount"]) == amount and
        row["Description"] == description
    )]
    if len(updated) == len(expenses):
        raise HTTPException(status_code=404, detail="Expense not found")
    
    # Write updated file
    with open(FILENAME, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["Date", "Category", "Amount", "Description"])
        writer.writeheader()
        writer.writerows(updated)
    
    return {"message": "Expense deleted successfully"}