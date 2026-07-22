from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from dotenv import load_dotenv
import os
from urllib.parse import quote

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Points explicitly to backend/.env
dotenv_path = os.path.join(BASE_DIR, '.env')

load_dotenv(dotenv_path)
password = quote(os.getenv('DB_PASSWORD'))
engine = create_engine(f"postgresql+psycopg://{os.getenv('DB_USER')}:{password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
