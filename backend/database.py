from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from dotenv import load_dotenv
import os
from urllib.parse import quote

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)

password = quote(os.getenv('DB_PASSWORD'))
engine = create_engine(
    f"postgresql+psycopg://{os.getenv('DB_USER')}:{password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
    pool_size=20,  # Maintain 20 connections
    max_overflow=40,  # Allow up to 40 overflow connections
    pool_pre_ping=True  # Verify connections before reusing
)

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()