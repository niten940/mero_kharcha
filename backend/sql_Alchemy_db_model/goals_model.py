from sqlalchemy import Column, ForeignKey
from sqlalchemy import *
from sql_Alchemy_db_model.base import Base


class Goals(Base):
    __tablename__ = "goals"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, server_default="other")
    current_amount = Column(Numeric(10, 2), nullable=False, default=0)
    goal_amount = Column(Numeric(10, 2), nullable=False)
    description = Column(Text)
    target_date = Column(Date, nullable=False)
    image_path = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    status = Column(String(20), nullable=False, server_default="active")  # active, completed
