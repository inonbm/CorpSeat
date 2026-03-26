import sqlite3
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dal.db import get_db_connection
from dal import office_dal, employee_dal

@pytest.fixture
def db():
    conn = get_db_connection(':memory:')
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'dal', 'schema.sql')
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    yield conn
    conn.close()

def test_office_crud(db):
    o_id = office_dal.create_office(db, 1, 101, 10)
    assert o_id is not None
    
    office = office_dal.get_office(db, o_id)
    assert office['floor'] == 1
    
    offices = office_dal.get_all_offices(db)
    assert len(offices) == 1
    
    rows_affected = office_dal.update_office(db, o_id, 1, 101, 20)
    assert rows_affected == 1
    office = office_dal.get_office(db, o_id)
    assert office['capacity'] == 20
    
    rows_affected = office_dal.delete_office(db, o_id)
    assert rows_affected == 1
    assert office_dal.get_office(db, o_id) is None

def test_employee_crud(db):
    e_id = employee_dal.create_employee(db, "Alice", "IT", "2023-01-01", 5000)
    assert e_id is not None
    
    emp = employee_dal.get_employee(db, e_id)
    assert emp['name'] == "Alice"
    
    all_emps = employee_dal.get_all_employees(db)
    assert len(all_emps) == 1
    
    rows = employee_dal.update_employee(db, e_id, "Alice Updated", "HR", "2023-01-02", 6000, None)
    assert rows == 1
    emp = employee_dal.get_employee(db, e_id)
    assert emp['name'] == "Alice Updated"
    
    rows = employee_dal.delete_employee(db, e_id)
    assert rows == 1
    assert employee_dal.get_employee(db, e_id) is None

def test_edge_case_delete_non_existent(db):
    assert office_dal.delete_office(db, 999) == 0
    assert employee_dal.delete_employee(db, 999) == 0

def test_edge_case_get_employees_for_empty_office(db):
    o_id = office_dal.create_office(db, 2, 201, 5)
    emps = employee_dal.get_employees_by_office(db, o_id)
    assert len(emps) == 0

def test_edge_case_get_employees_for_non_existent_office(db):
    emps = employee_dal.get_employees_by_office(db, 999)
    assert len(emps) == 0

def test_edge_case_update_with_invalid_data(db):
    o_id = office_dal.create_office(db, 3, 301, 10)
    with pytest.raises(sqlite3.IntegrityError):
        office_dal.update_office(db, o_id, 3, 301, -5) # negative capacity fails constraint

def test_edge_case_on_delete_set_null_with_pragma(db):
    o_id = office_dal.create_office(db, 4, 401, 5)
    e_id = employee_dal.create_employee(db, "Bob", "IT", "2023-01-01", 5000, o_id)
    
    emp = employee_dal.get_employee(db, e_id)
    assert emp['office_id'] == o_id
    
    office_dal.delete_office(db, o_id)
    
    emp = employee_dal.get_employee(db, e_id)
    assert emp['office_id'] is None
