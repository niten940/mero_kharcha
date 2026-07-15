"""
Expenses router — handles all expense-related routes for Mero Kharcha.
"""
from fastapi import HTTPException
from datetime import date
from pydantic import BaseModel
from database import get_db
from sqlalchemy.orm.session import Session
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends
from JWT_Authentication.auth import get_current_user
from sqlAlchemy.expense_models import Expenses

router_expense = APIRouter()

class ExpenseInput(BaseModel):
    title: str
    category: str
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

    if Expenses.user_id == current_user["user_id"]:
        return {"expense_id": expense_id}

@router_expense.get("/", summary="Return list of Expenses rows matching the given filters", description="Returns all expenses, optionally filtered by expense id and/or category")
def get_expense_Query(category:str | None = None, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Returns all expenses, optionally filtered by expense_id and/or category (case-insensitive).

    Args:
        category (str | None): Category name to filter by, if provided.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Returns:
        list: List of Expenses rows matching the given filters.
    """
    query = db.query(Expenses).filter(Expenses.user_id == current_user["user_id"]).order_by(Expenses.date.desc())
    if category:   query = query.filter(Expenses.category.ilike(category))
    return query.all() 

@router_expense.post("/post/", status_code=201, summary="Creates a new expense entry", description="Create new expense entry and return dictionary and status code: 201")
def create_expense(expense: ExpenseInput, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Create a new expense entry in the database.

    Args:
        expense (ExpenseInput): The expense data payload.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Returns:
        Expenses: The newly created expense record.
    """
    user_id = current_user["user_id"]
    add_expenses = Expenses(user_id= user_id,title= expense.title,amount=expense.amount,category=expense.category,description=expense.description, date= expense.date)
    db.add(add_expenses)
    db.commit()
    db.refresh(add_expenses)
    return add_expenses

@router_expense.put("/put/{expense_id}", summary="Update an existing expense", description="Updates all fields of an expense by ID. Returns 404 if the ID doesn't exist.")
def update_expense(expense: ExpenseInput,expense_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Update expense entry in the database.

    Args:
        expense (ExpenseInput): The expense data payload.
        expense_id (int) : id of expenses.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Raises:
        404 : Expenses id not found

    Returns:
        Updated data of the expense
    """
    expenses = db.query(Expenses).filter(Expenses.id == expense_id,Expenses.user_id == current_user["user_id"]).first()
    if not expenses:
        raise HTTPException(status_code=404, detail=f"Expenses id {expense_id} not found.")

    updating_data = expense.model_dump()
    for key, value in updating_data.items():
        setattr(expenses,key,value)
    db.commit()
    db.refresh(expenses)
    return expenses

@router_expense.delete("/dlt/{expense_id}", summary="Delete an expense", description="Deletes an expense by ID. Returns 404 if the ID doesn't exist.")
def delete_expense(expense_id: int, current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Delete expense entry in the database.

    Args:
        expense_id (int) : id of expenses.
        current_user (dict): The current authenticated user.
        db (Session): The database session.

    Raises:
        404 : Expenses id not found

    Returns:
        message: Expense id is deleted successfully.
    """
    expenses = db.query(Expenses).filter(Expenses.id == expense_id,Expenses.user_id == current_user["user_id"]).first()
    if not expenses:
        raise HTTPException(status_code=404, detail=f"Expenses id {expense_id} not found.")
    db.delete(expenses)
    db.commit()
    return {"message": f"Expense id {expense_id} is deleted successfully."}