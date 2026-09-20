import pytest
from app import app, load_courses

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_courses(client):
    response = client.get('/api/courses')
    assert response.status_code == 200
    assert response.get_json()['success'] is True

def test_create_course(client):
    payload = {
        "name": "Test Course",
        "description": "Unit Testing with PyTest"
    }
    response = client.post('/api/courses', json=payload)
    assert response.status_code == 201
    assert response.get_json()['data']['name'] == "Test Course"