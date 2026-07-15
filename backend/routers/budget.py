from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlAlchemy.expense_models import Expenses
from database import get_db

def check_budget_limit(category: str, limit: float, user_id: int, db: Session) -> dict:
    """
    Calculate category spending and check if it exceeds the budget limit.

    Args:
        category (str): Name of the category to check (case-insensitive).
        limit (float): The budget ceiling to check against.
        db (Session): The active SQLAlchemy database session.

    Returns:
        A dictionary containing spending totals, budget status, and overage amounts.
    """
    total_spent = round(float(db.query(func.sum(Expenses.amount)).filter(Expenses.user_id == user_id, Expenses.category.ilike(category)).scalar() or 0),2)
    over_budget = True if total_spent > limit else False
    remaining_balance = total_spent - limit
    amount_over = round(remaining_balance, 2) if total_spent > limit else 0
    return {"category": category,"total_spent": total_spent, "limit": limit, "over_budget": over_budget, "amount_over": amount_over}

def get_all_categorys_status(limit: float, db: Session) -> list :
    """
    Return budget status for every distinct category with recorded expenses.

    Args:
        limit (float): The shared budget ceiling applied to every category.
        db (Session): The active SQLAlchemy database session.

    Returns:
        list: A list of dicts, one per category, each in the same shape as check_budget_limit's return value.
    """
    category_list = db.query(Expenses.category).distinct().all()
    
    status_list = []
    for (dept_name,) in category_list:
        status = check_budget_limit(dept_name, limit, db)
        status_list.append(status)
        
    return status_list
    
if __name__ == "__main__":
    from database import get_db
    db = next(get_db())
    print(check_budget_limit("Office expenses", 5000, 3, db)) 
    print(check_budget_limit("Office expenses", 5000, 1, db))