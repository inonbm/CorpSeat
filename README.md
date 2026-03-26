# CorpSeat - Employees and Offices Management System

CorpSeat is a robust, full-stack management system built specifically without JavaScript, utilizing raw SQLite and Python/Flask to maintain strict server-side logic and processing.

## Project Structure
```text
CorpSeat/
├── app.py                   # Main Flask Application
├── corpseat.db              # SQLite Database (generated)
├── dal/                     # Data Access Layer (Raw SQL)
│   ├── db.py                # Connection Factory
│   ├── employee_dal.py      # Employee SQL Operations
│   ├── office_dal.py        # Office SQL Operations
│   └── schema.sql           # Database Table Definitions
├── routes/                  # Controller Layer
│   ├── api_routes.py        # JSON-only API (`/api/`)
│   └── ui_routes.py         # HTML/POST form routes (`/ui/`)
├── services/                # Business Logic Layer
│   ├── employee_service.py  # Employee Validation & Rules
│   └── office_service.py    # Office Matrix & Atomic Assignments
├── static/                  # Static Files
│   └── style.css            # Vanilla CSS (No Frameworks)
├── templates/               # Jinja2 HTML Templates
│   ├── base.html            # Core Base Template
│   ├── employees/           # Employee Views (List, Details, Form)
│   └── offices/             # Office Views (List, Details, Form, Assign)
└── tests/                   # Pytest Test Suites
    ├── test_api.py          # API Endpoint Tests
    ├── test_dal.py          # SQL Query Logic Tests
    ├── test_db.py           # Database Constraint Tests
    ├── test_integration.py  # End-to-End System Flow Tests
    ├── test_services.py     # Business Rules & Error States
    └── test_ui.py           # HTML Structure (No-JS Enforcement) Tests
```

## Installation & Deployment Options

You can deploy CorpSeat conventionally via Python environments or natively via Docker.

### Option A: Fully Containerized via Docker Compose (Recommended)
This approach automatically manages Dependencies, Gunicorn Production Web Servers, and Database bootstrapping utilizing ephemeral images mapped explicitly to persistent volumes.
1. **Clone the repository**
   ```bash
   git clone https://github.com/inonbm/CorpSeat.git
   cd CorpSeat
   ```
2. **Launch the Production Stack**
   ```bash
   docker compose up -d
   ```
   *The smart entrypoint script will automatically detect if `corpseat.db` exists in the `/app/data` volume. If missing, it immediately bootstraps your schema before serving traffic via Gunicorn.*
3. Open `http://localhost:5000/`

### Option B: Local Python Environment
1. **Clone the repository**
   ```bash
   git clone https://github.com/inonbm/CorpSeat.git
   cd CorpSeat
   ```
2. **Build Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Initialize Database natively**
   ```bash
   python3 -c "from dal.db import init_db; init_db()"
   ```
4. **Boot Development Server**
   ```bash
   python3 app.py
   ```
   Open `http://localhost:5000/`

## Testing Instructions
The system includes an extensive 24-test suite that validates data cascading, logic bounds, and HTTP rendering compliance.
```bash
source venv/bin/activate
pytest -v
```

## Architecture Decisions

* **Why raw SQL without an ORM?**
  Using Raw SQL allows immediate integration checking via `PRAGMA foreign_keys = ON;`, explicit definition of `ON DELETE SET NULL` cascades natively, explicit `CHECK` constraints on salaries/capacity, and complete visibility into the Data Access routines.
* **Why no JavaScript?**
  The requirement mandates a zero-JS frontend to completely separate complex processing from the client. All Filtering, Sorting, Pagination, and Validation metrics happen strictly on the server logic using Python algorithms and SQLite row returns, communicating purely through stateful HTML `POST/GET` rendering bindings via Jinja2 templates.
* **Strict Routing Namespace Rules:**
  To guarantee proper separation of concerns, boundaries have been established:
  * `/api/`: Responses emit JSON configurations exclusively standardizing `{data: [...], meta/pagination: {...}}` contracts. Only accepts JSON protocol boundaries.
  * `/ui/` (GET): Emits `text/html` structures exclusively rendering template layouts globally.
  * `/ui/` (POST): Accepts structural `form/urlencoded` payloads updating the core states, explicitly ending exclusively in `301/302 Redirects` avoiding any mixed protocol streams.
