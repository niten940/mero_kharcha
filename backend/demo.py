from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from urllib.parse import quote

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Points explicitly to backend/.env
dotenv_path = os.path.join(BASE_DIR, '.env')

load_dotenv(dotenv_path)
password = quote(os.getenv('DB_PASSWORD'))
print(f"psql -h {os.getenv('DB_USER')} -p 5432 -U {os.getenv('DB_USER')} -d {os.getenv('DB_NAME')}")