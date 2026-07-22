import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import expenses, incomes, budget
from JWT_Authentication import auth

app = FastAPI(
    title="Mero Kharcha",
    version="1.0.0",
    description="Personal expense tracking system. Manage expenses, incomes, budgets, and department-wise reports. Built with FastAPI and PostgreSQL."
)

# --- Enable CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from your Vue dev server (e.g. http://localhost:5174)
    allow_credentials=True,
    allow_methods=["*"],    # Allows GET, POST, PUT, DELETE, OPTIONS, etc.
    allow_headers=["*"],    # Allows custom headers like Authorization
)

# --- Include Routers ---
app.include_router(expenses.router_expense, prefix="/expenses", tags=["Expenses"])
app.include_router(incomes.router_income, prefix="/incomes", tags=["Incomes"])
app.include_router(auth.router_login, prefix="/auth_login", tags=["Auth"])

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