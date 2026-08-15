import uvicorn
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from rate_limiter import limiter
from JWT_Authentication import auth, profile_updates, register, login, forgot_password, token_refresh
from routers import (
    expenses, incomes, reports, goals, recurring, budget, 
    import_statement, goal_deposit, behavior, opportunity_cost, 
    calendar_bs, admin, ocr_receipt, financial_health, images
)

app = FastAPI(
    title="Mero Kharcha",
    version="1.0.0",
    description="Personal expense tracking system API",
)

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS for local web browsers, Vite dev servers, and Capacitor/Android Emulators
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use "*" during development to prevent emulator CORS block
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth Routes
app.include_router(register.router_register, prefix="/auth", tags=["Register"])
app.include_router(login.router_auth_login, prefix="/auth", tags=["Login"])
app.include_router(forgot_password.router_forgot_password, prefix="/auth", tags=["Password Reset"])
app.include_router(token_refresh.router_token, prefix="/auth", tags=["Token Refresh"])
app.include_router(profile_updates.router_profile, prefix="/auth", tags=["Auth"])
app.include_router(images.router_images, prefix="/images", tags=["Images"])

# Business Logic Routes
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
app.include_router(opportunity_cost.router_opportunity_cost, prefix="/opportunity-cost", tags=["Opportunity Cost"])
app.include_router(calendar_bs.router_calendar_bs, prefix="/calendar", tags=["Bikram Sambat Calendar"])
app.include_router(ocr_receipt.router_ocr, prefix="/ocr", tags=["OCR Receipt Scanning"])
app.include_router(admin.router_admin, prefix="/admin", tags=["Admin"])



@app.get("/")
def read_root():
    return {"message": "Welcome to Mero Kharcha API"}

@app.get("/status")
def get_status():
    return {"api": "Mero-Kharcha", "status": "running"}

if __name__ == "__main__":
    # Binding to 0.0.0.0 makes the server reachable to Android's 10.0.2.2 virtual bridge
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)