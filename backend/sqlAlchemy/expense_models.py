from sqlalchemy import *
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Expenses(Base):
    """
    SQLAlchemy model representing the 'expenses' table.

    Columns:
        id (int): Primary key, auto-incrementing.
        title (str): Short name/label for the expense.
        amount (Numeric): Expense amount, stored as a fixed 2-decimal value.
        category (str): Expense category (e.g. travel, supplies).
        department (str): Department that incurred the expense.
        description (str): Longer free-text detail of the expense.
        date (Date): Date the expense occurred.
        created_at (TIMESTAMP): Row creation timestamp, set by the database.
    """
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    amount = Column(Numeric(10,2), nullable=False)
    category = Column(String(100))
    department = Column(String(100))
    description = Column(Text)
    date = Column(Date)
    created_at = Column(TIMESTAMP, server_default=func.now())
