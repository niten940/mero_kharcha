"""
Incomes router — handles all income-related routes for Mero Kharcha.
"""
from pydantic import BaseModel
from starlette.responses import JSONResponse
from fastapi import APIRouter

router_income = APIRouter()

class IncomeInput(BaseModel):
    title: str
    amount: float
    description: str
    received_from: str

@router_income.post("/", status_code= 201,summary= "Creates new income entry", description= "Creates new income entry and return dictionary and status code: 201")
def create_income(income: IncomeInput):
    """
    Create a new income entry for the system. Take data as: title: str, amount: float, description: str, received_from: str

    Args:
    income(IncomeInput): body where data is sent

    Return:
    dict: All field and status create.
    """
    return {"title": income.title, "amount": income.amount, "description": income.description, "received_from": income.received_from, "status": "created"}

