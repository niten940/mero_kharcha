"""
User model — represents registered users for Mero Kharcha authentication.
"""
from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(100), nullable=True)
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    currency = Column(String(10), default="NPR", nullable=False)
    nationality = Column(String(50), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())