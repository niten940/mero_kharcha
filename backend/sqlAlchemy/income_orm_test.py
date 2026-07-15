from sqlalchemy.orm import sessionmaker,Session
from sqlalchemy import create_engine
from income_model import Income
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
    Queries and prints all incomes, or a message if the table is empty.

    Returns:
        None
    """
    select_incomes = session.query(Income).order_by().all()
    if not select_incomes:
        print("No incomes found.")
        return
    for income in select_incomes:
        print(f"ID: {income.id} | Title: {income.title} | Amount: Rs.{income.amount:.2f} | Description: {income.description}| Received From: {income.received_from}")

add_income = Income(title="Payment",amount=20000,description="Received from Shinji for sales of product",received_from="Shinji")
session.add(add_income)
session.commit()
print(f"Added income {add_income.title} - Rs.{add_income.amount:.2f}")

select_operation()

update_income = session.query(Income).filter(Income.id == 1).first()
update_income.amount = 40000
session.commit()
print(f"Update Income of {update_income.id} to new Rs.{update_income.amount:.2f}")
select_operation()

delete_income = session.query(Income).filter(Income.id == 1).first()
session.delete(delete_income)
session.commit()
print(f"Deleted income: ID: {delete_income.id}")
select_operation()

session.close()