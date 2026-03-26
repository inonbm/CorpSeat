import pytest
from datetime import date, timedelta
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from dal.db import get_db_connection
from dal import office_dal, employee_dal
from services import employee_service, office_service

@pytest.fixture
def db():
    conn = get_db_connection(':memory:')
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'dal', 'schema.sql')
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    yield conn
    conn.close()

def test_seniority_calculations(db):
    today = date.today()
    e_id1 = employee_service.create_employee(db, "A", "IT", today.strftime("%Y-%m-%d"), 5000)
    
    one_yr_ago = today - timedelta(days=365)
    e_id2 = employee_service.create_employee(db, "B", "IT", one_yr_ago.strftime("%Y-%m-%d"), 5000)
    
    emp1 = employee_service.get_employee(db, e_id1)
    emp2 = employee_service.get_employee(db, e_id2)
    
    assert emp1['seniority'] == 0
    assert emp2['seniority'] >= 1  # 1 or higher due to leap years

def test_future_hire_date_rejected(db):
    tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    with pytest.raises(ValueError, match="future"):
        employee_service.create_employee(db, "C", "IT", tomorrow, 5000)

def test_validators(db):
    today = date.today().strftime("%Y-%m-%d")
    with pytest.raises(ValueError, match="salary"):
        employee_service.create_employee(db, "D", "IT", today, -100)
    with pytest.raises(ValueError, match="capacity"):
        office_service.create_office(db, 1, 101, 0)

def test_assignment_reassignment(db):
    today = date.today().strftime("%Y-%m-%d")
    o_id1 = office_service.create_office(db, 1, 100, 5)
    o_id2 = office_service.create_office(db, 1, 101, 5)
    e_id = employee_service.create_employee(db, "E", "IT", today, 5000)
    
    office_service.assign_employees_to_office(db, o_id1, [e_id])
    assert employee_service.get_employee(db, e_id)['office_id'] == o_id1
    
    office_service.assign_employees_to_office(db, o_id2, [e_id])
    assert employee_service.get_employee(db, e_id)['office_id'] == o_id2

def test_assignment_overcapacity(db):
    today = date.today().strftime("%Y-%m-%d")
    o_id = office_service.create_office(db, 2, 201, 1) # capacity 1
    e_id1 = employee_service.create_employee(db, "F1", "IT", today, 5000)
    e_id2 = employee_service.create_employee(db, "F2", "IT", today, 5000)
    
    # Assign 2 employees to capacity 1 -> Overcapacity allowed! No error.
    office_service.assign_employees_to_office(db, o_id, [e_id1, e_id2])
    
    emps_in_office = employee_dal.get_employees_by_office(db, o_id)
    assert len(emps_in_office) == 2

def test_assignment_atomic_failure(db):
    today = date.today().strftime("%Y-%m-%d")
    o_id = office_service.create_office(db, 3, 301, 5)
    e_id = employee_service.create_employee(db, "G", "IT", today, 5000)
    db.commit()
    
    with pytest.raises(ValueError, match="do not exist"):
        office_service.assign_employees_to_office(db, o_id, [e_id, 999])
        
    assert employee_service.get_employee(db, e_id)['office_id'] is None
