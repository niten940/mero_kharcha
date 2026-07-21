import uvicorn
from fastapi import FastAPI
from routers import expenses, incomes, reports, goals, recurring
from JWT_Authentication import auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mero Kharcha",
    version="1.0.0",
    description="Personal expense tracking system. Manage expenses, incomes, budgets, and department-wise reports. Built with FastAPI and PostgreSQL.",
)

origin = [
    "http://localhost:3000",  # FastAPI hosting address
    "http://localhost:5173",  # default Vue.js hosting address
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router_login, prefix="/auth", tags=["Auth"])
app.include_router(expenses.router_expense, prefix="/expenses", tags=["Expenses"])
app.include_router(incomes.router_income, prefix="/incomes", tags=["Incomes"])
app.include_router(goals.router_goals, prefix="/goals", tags=["Goals"])
app.include_router(reports.router_reports, prefix="/reports", tags=["Reports"])
app.include_router(recurring.router_recurring, prefix="/recurring", tags=["Recurring"])


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


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=3000, reload=True)
