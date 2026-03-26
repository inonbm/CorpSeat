def create_employee(conn, name, department, hire_date, salary, office_id=None):
    cur = conn.execute(
        "INSERT INTO employees (name, department, hire_date, salary, office_id) VALUES (?, ?, ?, ?, ?)",
        (name, department, hire_date, salary, office_id)
    )
    return cur.lastrowid

def get_employee(conn, employee_id):
    return conn.execute("SELECT * FROM employees WHERE id = ?", (employee_id,)).fetchone()

def get_all_employees(conn):
    return conn.execute("SELECT * FROM employees").fetchall()

def update_employee(conn, employee_id, name, department, hire_date, salary, office_id):
    cur = conn.execute(
        "UPDATE employees SET name = ?, department = ?, hire_date = ?, salary = ?, office_id = ? WHERE id = ?",
        (name, department, hire_date, salary, office_id, employee_id)
    )
    return cur.rowcount

def delete_employee(conn, employee_id):
    cur = conn.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    return cur.rowcount

def get_employees_by_office(conn, office_id):
    return conn.execute("SELECT * FROM employees WHERE office_id = ?", (office_id,)).fetchall()

def get_employees_by_ids(conn, employee_ids):
    if not employee_ids:
        return []
    placeholders = ','.join(['?'] * len(employee_ids))
    return conn.execute(f"SELECT * FROM employees WHERE id IN ({placeholders})", tuple(employee_ids)).fetchall()

def update_employee_office(conn, employee_id, office_id):
    cur = conn.execute("UPDATE employees SET office_id = ? WHERE id = ?", (office_id, employee_id))
    return cur.rowcount
