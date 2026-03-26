import sqlite3
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dal.db import get_db_connection

@pytest.fixture
def db():
    conn = get_db_connection(':memory:')
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'dal', 'schema.sql')
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    yield conn
    conn.close()

def test_pragma_foreign_keys_active(db):
    cur = db.cursor()
    cur.execute("PRAGMA foreign_keys;")
    result = cur.fetchone()[0]
    assert result == 1, "PRAGMA foreign_keys is not active!"

def test_valid_inserts(db):
    cur = db.cursor()
    cur.execute("INSERT INTO offices (floor, room_number, capacity) VALUES (1, 101, 5)")
    office_id = cur.lastrowid
    
    cur.execute("INSERT INTO employees (name, department, hire_date, salary, office_id) VALUES ('Alice', 'Engineering', '2023-01-01', 5000, ?)", (office_id,))
    employee_id = cur.lastrowid
    
    assert office_id is not None
    assert employee_id is not None

def test_invalid_inserts_salary(db):
    cur = db.cursor()
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO employees (name, department, hire_date, salary, office_id) VALUES ('Bob', 'HR', '2023-01-01', 0, NULL)")

def test_invalid_inserts_capacity(db):
    cur = db.cursor()
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO offices (floor, room_number, capacity) VALUES (2, 201, 0)")

def test_duplicate_floor_room(db):
    cur = db.cursor()
    cur.execute("INSERT INTO offices (floor, room_number, capacity) VALUES (3, 301, 10)")
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO offices (floor, room_number, capacity) VALUES (3, 301, 5)")

def test_fk_violation(db):
    cur = db.cursor()
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO employees (name, department, hire_date, salary, office_id) VALUES ('Charlie', 'Sales', '2023-01-01', 3000, 999)")

def test_delete_office_sets_null(db):
    cur = db.cursor()
    cur.execute("INSERT INTO offices (floor, room_number, capacity) VALUES (4, 401, 5)")
    office_id = cur.lastrowid
    cur.execute("INSERT INTO employees (name, department, hire_date, salary, office_id) VALUES ('Dave', 'Marketing', '2023-01-01', 4000, ?)", (office_id,))
    employee_id = cur.lastrowid
    
    # Verify assignment
    cur.execute("SELECT office_id FROM employees WHERE id = ?", (employee_id,))
    assert cur.fetchone()['office_id'] == office_id
    
    # Delete office
    cur.execute("DELETE FROM offices WHERE id = ?", (office_id,))
    
    # Verify employee's office_id is NULL
    cur.execute("SELECT office_id FROM employees WHERE id = ?", (employee_id,))
    assert cur.fetchone()['office_id'] is None
