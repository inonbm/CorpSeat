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

def test_no_javascript_in_html(client):
    routes = [
        '/ui/offices',
        '/ui/offices/new',
        '/ui/employees',
        '/ui/employees/new',
        '/ui/assign'
    ]
    for r in routes:
        res = client.get(r)
        if res.status_code == 200:
            html = res.get_data(as_text=True).lower()
            assert '<script' not in html, f"JavaScript found in {r}"
