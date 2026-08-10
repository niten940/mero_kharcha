from sqlalchemy import Column, ForeignKey
from sqlalchemy import *
from sql_Alchemy_db_model.base import Base


class Goal_Deposit(Base):
    __tablename__ = "goal_deposits"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    id = Column(Integer, primary_key=True, autoincrement=True)
    amount = Column(Numeric(10, 2), nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
