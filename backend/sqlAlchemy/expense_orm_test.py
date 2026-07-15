from expense_models import Expenses
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

load_dotenv(".env")
password = quote_plus(os.getenv('DB_PASSWORD'))
engine = create_engine(f"postgresql+psycopg2://{os.getenv('DB_USER')}:{password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

Session = sessionmaker(bind=engine)
session = Session()
def select_operation():
    """
    Queries and prints all expenses, or a message if the table is empty.

    Returns:
        None
    """
    select_expenses = session.query(Expenses).order_by().all()
    if not select_expenses:
        print("No expenses found.")
        return
    for expense in select_expenses:
        print(f"ID: {expense.id} | Title: {expense.title} | Amount: Rs.{expense.amount:.2f} | Category: {expense.category} | Department: {expense.department} | Description: {expense.description}")
        
if __name__ == "__main__":
    add_expenses = Expenses(title='Food',amount=15000,category='Office expenses',department='IT',description='Celebrated the event finish.')
    session.add(add_expenses)
    session.commit()
    print(f"Added: {add_expenses.title} - Rs.{add_expenses.amount:.2f}")

    select_operation()
    print(" ")
    update_expenses = session.query(Expenses).filter(Expenses.id == 5).first()
    update_expenses.amount = 2000
    session.commit()
    select_operation()
    print(f"Updated ID {update_expenses.id}: new amount Rs.{update_expenses.amount:.2f}")

    delete_expenses = session.query(Expenses).filter(Expenses.id == 5).first()
    session.delete(delete_expenses)
    session.commit()
    select_operation()
    print(f"Deleted expense with ID {delete_expenses.id}")

    session.close()