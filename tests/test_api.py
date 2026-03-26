import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_namespaces(client):
    res = client.get('/api/offices')
    assert res.status_code == 200
    assert res.content_type == 'application/json'
    
    res = client.post('/ui/offices', data={'floor': '10', 'room_number': '100', 'capacity': '5'})
    assert res.status_code in [301, 302]
    
    res = client.get('/ui/offices')
    assert res.status_code == 200
    assert 'text/html' in res.content_type

def test_pagination_and_sorting_validation(client):
    res = client.get('/api/employees?limit=0')
    assert res.status_code == 400
    
    res = client.get('/api/employees?sort=badfield')
    assert res.status_code == 400
    
    res = client.get('/api/employees?page=999999&limit=10')
    assert res.status_code == 200
    data = res.get_json()
    assert data['data'] == []
    assert data['pagination']['page'] == 999999
