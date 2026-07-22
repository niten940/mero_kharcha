"""
Database initialization script.
Run this once to create all tables if they don't exist.
"""
from database import engine
from sqlAlchemy.user_models import Base

# Create all tables
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully!")
print("Tables created:")
print("  - users")
