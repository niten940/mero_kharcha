# Mero Kharcha

**Your personal expense tracker for Nepal, built around how you actually spend.**

Track expenses and incomes, set budgets and goals, import real bank and wallet
statements, and measure the health of your finances — with full support for the
Bikram Sambat calendar and NPR.

</div>

## Table of Contents

- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Author](#author)

## About

"*Mero Kharcha*" means "**My Expenses**" in Nepali. It is a personal finance
application that helps people in Nepal understand where their money goes.

Instead of forcing you to hand-enter every transaction, Mero Kharcha is built
around the tools you actually use:

- Import your **eSewa**, **Khalti**, and **Sajilo eBanking** statements directly.
- Scan physical receipts with your camera (printed or handwritten).
- Work in **Bikram Sambat** dates alongside the Gregorian calendar.
- Track everything in **NPR**.

The project started as a university capstone and has grown into a full
full-stack application with an analytics layer (financial health score, behavior
analysis, opportunity cost) on top of a simple CRUD core.

## Features

- **Expense & income tracking** — add, edit, delete, and categorize transactions.
- **Automatic categorization** — keyword-based auto-tagging that understands
  Nepali payment descriptions from eSewa, Khalti, and Sajilo eBanking.
- **Bank & wallet statement imports** — parse CSV, XLS, XLSX, and PDF statements
  from eSewa, Khalti, and Sajilo eBanking.
- **OCR receipt scanning** — offline (Tesseract) for printed text.
- **Budgets** — per-category budget limits.
- **Goals** — savings goals with scheduled deposits and a rolling-average
  velocity engine for projected completion.
- **Recurring transactions** — handle rent, subscriptions, EMI, and similar,
  with multi-cycle auto-fire catch-up.
- **Bikram Sambat calendar** — AD to BS and BS to AD conversion.
- **Behavior analysis** — month-over-month comparisons, spending distribution,
  top categories, and multi-period trends.
- **Opportunity cost calculator** — see the compounded future value of money you
  spend instead of invest.
- **Reports** — category-wise and period-wise expense reports.
- **Secure authentication** — JWT access/refresh tokens with Google OAuth login,
  password reset, and rate limiting.
- **Admin panel** — read-only administrative monitoring (no access to other
  users' financial records).

## Tech Stack

| Layer        | Technology                                                    |
| ------------ | -------------------------------------------------------------- |
| Backend      | Python, FastAPI, uvicorn                                       |
| API          | REST, OpenAPI (auto-generated docs at `/docs`)                 |
| Database     | PostgreSQL, SQLAlchemy                                          |
| Auth         | JWT (python-jose), bcrypt, Google OAuth, slowapi rate limiting  |
| File parsing | pandas, openpyxl, pdfplumber                                    |
| OCR          | pytesseract, Pillow                                              |
| Calendar     | `nepali-datetime` (Bikram Sambat)                                |
| Frontend     | Vue 3, Quasar (mobile application, per supervisor direction)     |

## Project Structure

```
mero_kharcha/
└── backend/
    ├── main.py                    # App entry point, router wiring, CORS
    ├── database.py                # PostgreSQL engine + session factory
    ├── category_rules.py          # Keyword -> category auto-tagging rules
    ├── rate_limiter.py            # Shared slowapi limiter instance
    ├── routers/
    │   ├── expenses.py            # Expense CRUD + auto-categorization
    │   ├── incomes.py             # Income CRUD
    │   ├── reports.py             # Monthly / category summaries
    │   ├── goals.py               # Goal CRUD + velocity-based progress
    │   ├── goal_deposit.py        # Goal deposit CRUD
    │   ├── recurring.py           # Recurring transaction CRUD + auto-fire
    │   ├── budget.py              # Budget CRUD + watchdog
    │   ├── import_statement.py    # Statement parser (CSV/XLSX/PDF)
    │   ├── behavior.py            # Financial behavior analysis
    │   ├── opportunity_cost.py    # Opportunity cost calculator
    │   ├── calendar_bs.py         # AD <-> BS calendar conversion
    │   ├── admin.py                # Read-only admin monitoring
    │   ├── ocr_receipt.py          # OCR receipt scanning
    ├── sql_Alchemy_db_model/       # SQLAlchemy ORM models
    │   ├── base.py
    │   ├── expense_models.py
    │   ├── income_model.py
    │   ├── user_models.py
    │   ├── goals_model.py
    │   ├── goal_deposit_model.py
    │   ├── recurring_model.py
    │   └── budget_model.py
    └── JWT_Authentication/
        ├── auth.py                # Shared token creation/validation core
        ├── register.py            # POST /auth/register
        ├── login.py                # POST /auth/login, /auth/login/google
        ├── forgot_password.py      # POST /auth/forgot-password, /reset-password
        └── token_refresh.py        # POST /auth/refresh
└── frontend/                       # Vue 3 + Quasar mobile application
    ├── src/
    │   ├── api.js                  # Axios instance with JWT interceptor
    │   ├── router/                 # Vue Router routes
    │   ├── stores/                 # Pinia stores
    │   ├── pages/                  # Dashboard, Goals, Login, Signup,
    │   │                           # Reset Password, Imports, Privacy, Terms
    │   └── components/             # Shared components
    ├── vite.config.js
    └── package.json
```

## Author

Developed by the Mero Kharcha team:
- **Rijan Ban**
- **Sambad Shakya**
- **Nitendra Bajracharya**
