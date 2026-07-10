from posixpath import pardir
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


def add_expenses(title,amount,category, department,description):
    """
    Creates new expense to the mero_kharcha PostgreSQL database.

    Args:
        title (str): Title of the expense.
        amount (float): Expense amount in rupees.
        category (str): Expense category.
        department (str): Department the expense belongs to.
        description (str): Additional details about the expense.
    
    Returns: None
    
    """
    conn_insert = get_connection()
    cursor = conn_insert.cursor()
    cursor.execute("INSERT INTO expenses(title, amount, category,department,description) VALUES (%s,%s,%s,%s,%s)",(title,amount,category,department,description))
    conn_insert.commit()
    cursor.close()
    conn_insert.close()
    print("New expenses added successfully.")

def get_expense():
    """
    Select and returns existing expense from the mero_kharcha PostgreSQL database.
    
    Returns: expenses: Exisiting expense will be returned from the expense table in mero_kharcha.
    
    """
    conn_read = get_connection()
    cursor = conn_read.cursor()
    cursor.execute("SELECT * FROM expenses")
    data = cursor.fetchall()
    for info in data:
        print(f"ID: {info[0]} | Title: {info[1]} | Amount: Rs.{info[2]:.2f} | Category: {info[3]} | Department: {info[4]} | Description: {info[5]}")
    cursor.close()
    conn_read.close()
    print("Expenses returned successfully")

def update_expense(exp_id, new_amount):
    """
    Update expense in the mero_kharcha PostgreSQL database.

    Args:
        exp_id(int): ID of the expense
        new_amount (float): Expense amount in rupees.

    Returns: None
    
    """
    conn_update = get_connection()
    cursor = conn_update.cursor()
    cursor.execute("UPDATE expenses SET amount = %s WHERE id= %s ",(new_amount,exp_id,))
    conn_update.commit()
    cursor.close()
    conn_update.close()
    print("Expenses has been updated.")

def delete_expense(exp_id):
    """
    Delete selected expense to the mero_kharcha PostgreSQL database.
    
    Args:
        id(int): ID of the expense.
        
    Returns: None
    
    """
    conn_delete = get_connection()
    cursor = conn_delete.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = %s",(exp_id,))
    conn_delete.commit()
    cursor.close()
    conn_delete.close()
    print("Expenses has been deleted.")

try: 
    add_expenses('Stationary',1500,'Office expenses','IT','Stationary item purchased')
    get_expense()
    update_expense(1,2000)
    get_expense()
    delete_expense(1)
    get_expense()
except Exception as e:
    print(f"Error occured! Error: {e}")
finally:
    print("CRUD operation executed!!")