import uvicorn
from fastapi import FastAPI
from routers import expenses, incomes

if __name__ == "__main__":
    uvicorn.run(app="main:app",host="0.0.0.0",port=3000,reload=True)

app = FastAPI(
    title="Mero Kharcha",
    version="1.0.0",
    description="Organizational expense tracking system. Manage expenses, incomes, budgets, and department-wise reports. Built with FastAPI and PostgreSQL."
)

app.include_router(expenses.router_expense,prefix="/expenses", tags=["Expenses"])
app.include_router(incomes.router_income,prefix="/incomes", tags=["Incomes"])

@app.get("/")
def read_root():
    """
    Returns a welcome message for the Mero Kharcha API.
    """
    return {"message": "Welcome, user to Mero Kharcha"}


@app.get("/status")
def get_status():
    """
    Returns the API name and current running status.
    """
    return {"api": "Mero-Kharcha", "status": "running"}