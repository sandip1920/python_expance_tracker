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

# Simple menu
while True:
    print("\nPersonal Expense Tracker")
    print("1. Add Expense")
    print("2. Exit")
    choice = input("Choose an option: ")

    if choice == '1':
        add_expense()
    elif choice == '2':
        break
    else:
        print("Invalid choice. Try again.")