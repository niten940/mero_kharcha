from dotenv import load_dotenv
import psycopg2
import os

def get_connection():
    """
    Creates and returns a connection to the mero_kharcha PostgreSQL database.
    
    Returns: connection: A psycopg2 connection object to the mero_kharcha database.
    
    """

    load_dotenv(".env")
    conn = psycopg2.connect(host = os.getenv("DB_HOST"), port = os.getenv("DB_PORT") , dbname = os.getenv("DB_NAME"), user= os.getenv("DB_USER"), password= os.getenv("DB_PASSWORD"))
    return conn

if __name__ == "__main__":
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT current_database()")
    result = cursor.fetchone()

    print(f"Current Database: {result}")
    cursor.close()
    conn.close()
    print("Connection closed.")