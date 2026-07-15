"""
Expenses router — handles all expense-related routes for Mero Kharcha.
"""
from datetime import date
from pydantic import BaseModel
from database import get_db
from sqlalchemy.orm.session import Session
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends
from JWT_Authentication.auth import get_current_user,require_admin
from sqlAlchemy.expense_models import Expenses

router_expense = APIRouter()

class ExpenseInput(BaseModel):
    title: str
    category: str
    department: str
    amount: float
    date: date
    description: str

@router_expense.get("/{expense_id}",summary="Return expense ID", description="When this API is hit, it returns expense ID")
def get_expense_ID(expense_id: int, current_user: str = Depends(get_current_user),db: Session = Depends(get_db)):
    """
    Return single expense_id
    Return error if expense_id < 1
    """
    if expense_id < 1:
        return JSONResponse(
            status_code= 404,
            content= {"error":"Expense not found"}
        )
    return {"expense_id": expense_id}
    print("I entered here")

@router_expense.get("/", summary="Return 'all' or 'department_name'", description="Return 'all' if no query is sent through URL, return 'department_name' if department name is sent through URL")
def get_expense_Query(department: str = "",category:str = "", db: Session = Depends(get_db)):
    """
    Return department name, if query is none return all
    """
    query = db.query(Expenses).order_by()
    if department: query = query.filter(Expenses.department == department)
    if category:   query = query.filter(Expenses.category == category)
    return query.all() 

@router_expense.post("/post/", status_code=201, summary="Creates a new expense entry", description="Create new expense entry and return dictionary and status code: 201")
def create_expense(expense: ExpenseInput, current_user: dict = Depends(require_admin), db: Session = Depends(get_db)):
    """
    Create a new expense entry in the database.

    Args:
        expense (ExpenseInput): The expense data payload.
        current_user (dict): The current authenticated admin user.
        db (Session): The database session.

    Returns:
        Expenses: The newly created expense record.
    """

    add_expenses = Expenses(title= expense.title,amount=expense.amount,category=expense.category,department=expense.department,description=expense.description, date= expense.date)
    db.add(add_expenses)
    db.commit()
    db.refresh(add_expenses)
    return add_expenses