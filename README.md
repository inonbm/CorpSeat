# Employees and Offices Management System

## Phase 0: Requirements Analysis

### 1. Entities and Relationships
**Employee**
* `id` (PK, INTEGER)
* `name` (TEXT, NOT NULL)
* `department` (TEXT, NOT NULL)
* `hire_date` (TEXT, NOT NULL) - Must not be in the future (Validated in business logic only).
* `salary` (REAL, NOT NULL) - Must be > 0.
* `office_id` (FK → Office, nullable)
* `seniority` - Computed property: `floor((today - hire_date).days / 365)`, never stored in DB.

**Office**
* `id` (PK, INTEGER)
* `floor` (INTEGER, NOT NULL)
* `room_number` (INTEGER, NOT NULL)
* `capacity` (INTEGER, NOT NULL) - Must be > 0.
* Unique constraint on (floor, room_number).

**Relationships**
* One office can house many employees.
* An employee belongs to zero or one office.
* Office deletion: `ON DELETE SET NULL`. If an office is deleted, all its employees become unassigned.

**Capacity Behavior:**
`capacity` is informational strictly. It defines intended maximums, but does NOT act as a hard block during assignment. Overcapacity is a valid system state, reportable via API and highlightable via UI.

### 2. Constraints and Validation Rules
* **Database Layer:**
  * Strict Foreign Key enforcement via mandatory `PRAGMA foreign_keys = ON;` on every connection.
  * Check constraints: `salary > 0`, `capacity > 0`.
  * Unique pair constraint: `UNIQUE(floor, room_number)`.
* **Business Logic Layer:**
  * `hire_date` must not be in the future.
  * Verification of employee existence during assignment. If ANY provided `employee_id` is invalid, the entire assignment batch fails atomically (rollback).
  * Safe reassignment: Permitted explicitly. Target `office_id` is updated. No-op if they are already in the correct office.

### 3. Edge Cases Defined
* **Overcapacity Assignments:** A batch assignment pushing an office over capacity must successfully process. The state will be reflected in `/api/offices?filter=overcapacity`.
* **Atomic Failure:** Batch assignment where 2 IDs are valid and 1 is invalid -> None of the 3 IDs get processed (transaction rollback).
* **Office Deletion cascades gracefully:** No orphans, `office_id` safely `NULL`ed ensuring structural integrity without deleting employee records.
* **Seniority Edge Computation:** Leap years handling implicitly via typical Python libraries or raw computation of days. Exactly today = 0. Exactly 365 days ago = 1 year.
* **Future hire_date injection:** Blocked safely at service layer.

---

## Phase 1: Project Structure

### Directory Tree
```text
CorpSeat/
├── app.py                  # Application entry point and Flask initialization
├── dal/                    # Data Access Layer
│   ├── db.py               # Database connection and setup routines
│   ├── employee_dal.py     # Employee raw SQL queries
│   └── office_dal.py       # Office raw SQL queries
├── routes/                 # HTTP Routing Layer
│   ├── api_routes.py       # JSON API routes namespace (/api/)
│   └── ui_routes.py        # HTML/UI routes namespace (/ui/)
├── services/               # Business Logic Layer
│   ├── employee_service.py # Employee business logic and validation
│   └── office_service.py   # Office business logic, assignment, capacity rules
├── templates/              # HTML Templates (Hebrew text only)
│   ├── base.html
│   ├── employees/
│   │   ├── list.html
│   │   ├── details.html
│   │   └── form.html
│   └── offices/
│       ├── list.html
│       ├── details.html
│       ├── form.html
│       └── assign.html
└── static/                 # Static assets
    └── style.css           # Vanilla CSS only
```

### Responsibility Mapping
* **`routes/`**: Strictly handles HTTP requests, extracts parameters, standardizes standard responses, and delegates to the `services/` layer. It has zero knowledge of the database.
* **`services/`**: Computes business logic, validates rules (e.g., `hire_date` limit, positive salaries/capacities), checks atomic assignments, computes `seniority`, orchestrates workflows. No raw SQL or requests objects here.
* **`dal/`**: Executes raw SQLite queries (`INSERT`, `SELECT`, `UPDATE`, `DELETE`). It knows nothing about HTTP or business requirements (besides basic DB constraints).
* **`templates/`**: Renders dynamic HTML correctly representing internal data, filtering queries, and pagination values. Contains only Hebrew text.
* **`static/`**: Houses the strict Vanilla CSS handling styling, including state-based highlights (red rows for overcapacity offices).

### Namespace Handlers
* **`routes/api_routes.py`**: Exclusively handles all endpoints prefixed with `/api/`. It strictly returns standard JSON responses and JSON error payloads. No HTML.
* **`routes/ui_routes.py`**: Exclusively handles all endpoints prefixed with `/ui/`.
  * **GET** requests render HTML templates cleanly.
  * **POST** requests process UI mutations (forms) and return redirects to the appropriate `/ui/` pages. Never returns JSON.

---
*End of Phase 1 documentation.*

---

## Phase 2: Database Design

### SQL Schema (`dal/schema.sql`)
The underlying datastore exclusively uses strictly defined SQLite constraints.

```sql
CREATE TABLE offices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    floor INTEGER NOT NULL,
    room_number INTEGER NOT NULL,
    capacity INTEGER NOT NULL CHECK (capacity > 0),
    UNIQUE(floor, room_number)
);

CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    hire_date TEXT NOT NULL,
    salary REAL NOT NULL CHECK (salary > 0),
    office_id INTEGER NULL,
    FOREIGN KEY (office_id) REFERENCES offices(id) ON DELETE SET NULL
);
```

### Constraints & Integrity Rules
* **Foreign Keys Enforcement**: SQLite requires explicit PRAGMA definition to enable enforcement. `db.py` rigidly attaches `PRAGMA foreign_keys = ON;` on every connection.
* **Cascading Delete**: Validated `ON DELETE SET NULL` upon office removal ensures orphaned employees drop cleanly into the unassigned pool.
* **Check Validators**: DB strictly ensures `salary > 0` and `capacity > 0`.
* **Unique Spaces**: A `UNIQUE` constraint over `(floor, room_number)` guards against overlapping physical layouts.
* **Deferred Logic**: Due to SQLite restriction on dynamic checking, dates (`hire_date` limit) are shifted to application/business logic validation scope exclusively.

---
*End of Phase 2 documentation.*

---

## Phase 3: Data Access Layer

The Data Access layer explicitly isolates raw SQL queries away from the API/Services layer.
* **ORM Zero**: No Object-Relational Mapping (ORM) dependencies are utilized.
* **Direct Operations**: Implements CRUD functions via explicit raw parameterized queries, maximizing efficiency and protecting against SQL injections.
* **Connection Context**: Every DAL function ingests a SQLite connection object (`conn`), allowing the higher logic layers to tightly control Transactionality and Rollbacks while the DAL blindly safely executes SQL.
* **Key Implementations**:
  * `dal/office_dal.py`: `create_office`, `get_office`, `get_all_offices`, `update_office`, `delete_office`
  * `dal/employee_dal.py`: `create_employee`, `get_employee`, `get_all_employees`, `update_employee`, `delete_employee`, `get_employees_by_office`
* **Rigorous Validation**: Edge behaviors (invalid deletes yielding `0` rowcounts, fetching employees on empty/ghost offices returning native empty lists `[]`, and seamless cascading ON DELETE logic bounds) precisely tested within isolation.

---
*End of Phase 3 documentation.*

---

## Phase 4: Business Logic

The Business Logic layer securely orchestrates rules, limits, and dynamic computations away from the Data Access Layer, forming the core application intelligence.
* **Date & Limit Validations**: Explicit boundaries (`salary > 0`, `capacity > 0`, `hire_date <= today`) are strictly validated python-side before sending data to the DAL.
* **Dynamic Seniority**: `seniority` is evaluated dynamically upon retrieval (`floor((today - hire_date).days / 365)`). It is strictly a computed property, never stored persistently.
* **Permissive Capacity Rules**: While offices have defined capacities, the business layer explicitly permits *overcapacity*. Assignments bypassing capacity are allowed without triggering blocks or exceptions, relying rather on UI feedback.
* **Atomic Assignments**: Routing bulk employees to an office runs inside an explicit transaction block (`try/except/rollback`). Every single requested `employee_id` in the batch is evaluated safely. Should any target fail validation (e.g. non-existent employee), the entire operation rolls back, keeping prior statuses fully untouched.
* **Reassignments**: Direct reassignments override old `office_id` flawlessly, while assignments to already matching offices are gracefully caught and treated as efficient no-ops.

---
*End of Phase 4 documentation.*
