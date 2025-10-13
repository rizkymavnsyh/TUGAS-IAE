import pytest
from app import app  

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_login(client):
    response = client.post('/auth/login', json={"email": "user1@example.com", "password": "pass123"})
    
    assert response.status_code == 200
    
    assert "access_token" in response.json

def test_get_items(client):
    response = client.get('/items')
    
    assert response.status_code == 200
    
    assert "items" in response.json

def test_update_profile(client):
    login_response = client.post('/auth/login', json={"email": "user1@example.com", "password": "pass123"})
    token = login_response.json['access_token']  
    
    response = client.put('/profile', json={"name": "Updated Name", "email": "updated@example.com"},
                          headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    
    assert response.json["profile"]["name"] == "Updated Name"
    assert response.json["profile"]["email"] == "updated@example.com"

