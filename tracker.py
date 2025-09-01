import csv
import os
from datetime import datetime

FILENAME = 'expenses.csv'

# Create the file with headers if it doesn't exist
if not os.path.exists(FILENAME):
    with open(FILENAME, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Category', 'Amount', 'Note'])

def add_expense():
    date = input("Enter date (YYYY-MM-DD) or press Enter for today: ").strip()
    if not date:
        date = datetime.today().strftime('%Y-%m-%d')

    category = input("Enter category (e.g. Food, Transport): ").strip()
    amount = input("Enter amount: ").strip()
    note = input("Optional note: ").strip()

    try:
        amount = float(amount)
    except ValueError:
        print("Invalid amount. Please enter a number.")
        return

    with open(FILENAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([date, category, amount, note])

    print("Expense added successfully!")


def view_expenses():
    with open(FILENAME, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)


def category_expenses():
    total_expense = 0
    category = input("Enter category name:")
    with open(FILENAME, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1].lower() == category.lower():
                total_expense = total_expense + float(row[2])

    print(f"{category} category wise total expense: {total_expense}")     


def highlow_expense():
    high_expense = 0
    with open(FILENAME, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if high_expense < float(row[2]):
                high_expense = float(row[2])
                
    print(f"Highest expense: {high_expense}")


# Simple menu
while True:
    print("\nPersonal Expense Tracker")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Catategory wise Expenses")
    print("4. Highest & Lowest Expense")
    print("5. Exit")
    choice = input("Choose an option: ")

    if choice == '1':
        add_expense()
    elif choice == '2':
        view_expenses()
    elif choice == '3':
        category_expenses()
    elif choice == '4':
        highlow_expense()
    elif choice == '5':
        break
    else:
        print("Invalid choice. Try again.")