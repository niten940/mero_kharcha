"""
Expenses router — handles all expense-related routes for Mero Kharcha.
"""
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import APIRouter

router_expense = APIRouter()

class ExpenseInput(BaseModel):
    title: str
    category: str
    department: str
    amount: float
    description: str

@router_expense.get("/{expense_id}",summary="Return expense ID", description="When this API is hit, it returns expense ID")
def get_expense_ID(expense_id: int):
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

@router_expense.get("/", summary="Return 'all' or 'department_name'", description="Return 'all' if no query is sent through URL, return 'department_name' if department name is sent through URL")
def get_expense_Query(department: str = "all"):
    """
    Return department name, if query is none return all
    """
    return {"department": department}

@router_expense.post("/", status_code=201, summary="Creates a new expense entry", description="Create new expense entry and return dictionary and status code: 201")
def create_expense(expense: ExpenseInput):
    """
    Create a new expense entry for the system. takes data as: title: str, category: str, department: str, amount: float, description: str

    Args:
    expense(ExpenseInput): body where data is sent

    Return:
    dict: All field and status of the API
    """
    return {"title": expense.title, "category": expense.category, "amount": expense.amount, "department": expense.department, "description": expense.description, "status": "received"}