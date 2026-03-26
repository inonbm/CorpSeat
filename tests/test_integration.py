import pytest
from app import app
import sqlite3
import os
import tempfile
from datetime import date, timedelta

@pytest.fixture
def test_db_path():
    fd, path = tempfile.mkstemp()
    os.close(fd)
    yield path
    os.unlink(path)

@pytest.fixture
def client(monkeypatch, test_db_path):
    app.config['TESTING'] = True
    
    def mock_get_db_connection(*args, **kwargs):
        conn = sqlite3.connect(test_db_path, timeout=10)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn
        
    setup_conn = mock_get_db_connection()
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'dal', 'schema.sql')
    with open(schema_path, 'r') as f:
        setup_conn.executescript(f.read())
    setup_conn.close()
            
    monkeypatch.setattr('app.get_db_connection', mock_get_db_connection)
    
    with app.test_client() as client:
        yield client

def test_full_integration_flow(client):
    # 1. Create office (capacity 1)
    res = client.post('/api/offices', json={'floor': 10, 'room_number': 100, 'capacity': 1})
    assert res.status_code == 201
    office_id = res.get_json()['id']
    
    # 2. Create 2 employees (one hired today, one 2 years ago)
    today = date.today()
    two_yrs_ago = today - timedelta(days=365*2)
    
    res = client.post('/api/employees', json={'name': 'E1', 'department': 'Dev', 'hire_date': today.strftime("%Y-%m-%d"), 'salary': 1000})
    emp1_id = res.get_json()['id']
    
    res = client.post('/api/employees', json={'name': 'E2', 'department': 'HR', 'hire_date': two_yrs_ago.strftime("%Y-%m-%d"), 'salary': 1500})
    emp2_id = res.get_json()['id']
    
    # 3. Assign
    res = client.post('/api/assign', json={'office_id': office_id, 'employee_ids': [emp1_id, emp2_id]})
    assert res.status_code == 200
    
    # 4. Check overcapacity API JSON filter
    res = client.get('/api/offices?filter=overcapacity')
    data = res.get_json()['data']
    assert len(data) == 1
    assert data[0]['id'] == office_id
    
    # 5. Check overcapacity UI CSS class rendering in HTML dynamically
    res = client.get('/ui/offices')
    html = res.get_data(as_text=True)
    assert 'row-overcapacity' in html
    
    # 6. Seniority filters test natively
    res = client.get('/api/employees?min_seniority=2')
    data = res.get_json()['data']
    assert len(data) == 1 # only E2
    assert data[0]['id'] == emp2_id
    
    res = client.get('/api/employees?max_seniority=0')
    data = res.get_json()['data']
    assert len(data) == 1 # only E1
    assert data[0]['id'] == emp1_id
    
    # 7. Multi-step/Pagination tests (Sort Ascending checks)
    res = client.get('/api/employees?page=1&limit=1&sort=name&order=asc')
    data = res.get_json()
    assert len(data['data']) == 1
    assert data['pagination']['total'] == 2
    assert data['data'][0]['name'] == 'E1'
    
    # 8. Delete office -> verify ON DELETE SET NULL carries through full stack PRAGMA
    res = client.delete(f'/api/offices/{office_id}')
    assert res.status_code == 200
    
    res = client.get(f'/api/employees/{emp1_id}')
    assert res.get_json()['office_id'] is None
    
    # 9. Verify strict route namespaces
    
    # Verify UI mutations ONLY via POST (This route is strictly POST in code)
    res = client.get('/ui/offices/1/delete')
    assert res.status_code == 405  # Method Not Allowed
    
    # Zero JSON in UI GET response
    res = client.get('/ui/employees')
    assert 'application/json' not in res.content_type
    assert 'text/html' in res.content_type
    
    # Zero HTML in API responses
    res = client.get('/api/employees')
    assert 'text/html' not in res.content_type
    assert 'application/json' in res.content_type
