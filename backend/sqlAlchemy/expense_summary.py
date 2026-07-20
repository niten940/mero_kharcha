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

def get_total_expenses():
    """
    Queries all expenses and returns the sum of their amounts.

    Args:
        None

    Returns:
        Decimal: The total of all expense amounts.
    """
    total_expense = 0
    select_expense = session.query(Expenses).order_by().all()
    for expense in select_expense:
        total_expense += expense.amount

    return total_expense

if __name__ == "__main__":
    total_amount = get_total_expenses()
    print(f"Total expenses: Rs.{total_amount:.2f}")