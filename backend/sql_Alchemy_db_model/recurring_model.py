from sqlalchemy import Column, ForeignKey
from sqlalchemy import *
from sql_Alchemy_db_model.base import Base
from sqlalchemy import Enum as SqlEnum
from enum import Enum


class TransactionType(str, Enum):
    expense = "expense"
    income = "income"


class Frequency(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    yearly = "yearly"


class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(SqlEnum(TransactionType), nullable=False)
    title = Column(String(100), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    frequency = Column(SqlEnum(Frequency), nullable=False)
    next_due_date = Column(Date, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
