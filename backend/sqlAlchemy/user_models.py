"""
User model — represents registered users for Mero Kharcha authentication.
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, func
from sqlAlchemy.base import Base


class Users(Base):
    """
    Represents a registered user account.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(100), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
