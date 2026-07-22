from sqlAlchemy.base import Base
from sqlAlchemy.user_models import Users
from sqlalchemy import *


class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    amount = Column(NUMERIC(10, 2), nullable=False)
    description = Column(String(100))
    received_from = Column(String(100))
    date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
