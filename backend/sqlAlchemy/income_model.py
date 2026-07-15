from sqlalchemy.orm import declarative_base
from sqlalchemy import *

Base = declarative_base()

class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100),nullable=False)
    amount = Column(NUMERIC(10,2), nullable=False)
    description = Column(String(100))
    received_from = Column(String(100))