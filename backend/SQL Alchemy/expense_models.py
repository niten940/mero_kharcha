from sqlalchemy import *
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Expenses(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    amount = Column(Numeric(10,2), nullable=False)
    category = Column(String(100))
    department = Column(String(100))
    description = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())
