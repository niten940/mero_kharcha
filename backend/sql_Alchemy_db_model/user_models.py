"""
User model — represents registered users for Mero Kharcha authentication.
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func
from sql_Alchemy_db_model.base import Base


class Users(Base):
    """
    Represents a registered user account.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=False)
    currency = Column(String(10), nullable=False, default="NPR")
    nationality = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    hashed_password = Column(String(100), nullable=True)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())