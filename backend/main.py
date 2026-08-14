import uvicorn
from fastapi import FastAPI
from routers import (expenses, incomes, reports, goals, recurring, budget, import_statement, goal_deposit, behavior, opportunity_cost, calendar_bs, admin, ocr_receipt, financial_health)
from JWT_Authentication import auth, profile_updates
from fastapi.middleware.cors import CORSMiddleware
from rate_limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from JWT_Authentication import register, login, forgot_password, token_refresh


app = FastAPI(
    title="Mero Kharcha",
    version="1.0.0",
    description="Personal expense tracking system. Manage expenses, incomes, budgets, and category-wise reports. Built with FastAPI and PostgreSQL.",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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


#authentication routes
app.include_router(register.router_register, prefix="/auth", tags=["Register"])
app.include_router(login.router_auth_login, prefix="/auth", tags=["Login"])
app.include_router(forgot_password.router_forgot_password, prefix="/auth", tags=["Password Reset"])
app.include_router(token_refresh.router_token, prefix="/auth", tags=["Token Refresh"])
app.include_router(profile_updates.router_profile, prefix="/auth", tags=["Auth"])

#Functionality routes
app.include_router(expenses.router_expense, prefix="/expenses", tags=["Expenses"])
app.include_router(incomes.router_income, prefix="/incomes", tags=["Incomes"])
app.include_router(goals.router_goals, prefix="/goals", tags=["Goals"])
app.include_router(financial_health.router_financial_health, prefix="/health", tags=["Financial Health"])
app.include_router(import_statement.router_imports, prefix="/imports", tags=["Imports"])
app.include_router(recurring.router_recurring, prefix="/recurring", tags=["Recurring"])
app.include_router(budget.router_budget, prefix="/budget", tags=["Budget"])
app.include_router(reports.router_reports, prefix="/reports", tags=["Reports"])
app.include_router(goal_deposit.router_goal_deposit, prefix="/goal_deposit", tags=["Goal Deposit"])
app.include_router(behavior.router_behavior, prefix="/behavior", tags=["Behavior Analysis"])
app.include_router(opportunity_cost.router_opportunity_cost, prefix="/opportunity-cost", tags=["Opportunity Cost"],)
app.include_router(calendar_bs.router_calendar_bs, prefix="/calendar", tags=["Bikram Sambat Calendar"])

#Additional Functionality routes
app.include_router(ocr_receipt.router_ocr, prefix="/ocr", tags=["OCR Receipt Scanning"])
app.include_router(admin.router_admin, prefix="/admin", tags=["Admin"])

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
