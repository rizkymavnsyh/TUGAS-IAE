import pytest
from app import app  # Mengimpor aplikasi Flask Anda

# Fixture untuk membuat client Flask untuk pengujian
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Menguji login endpoint
def test_login(client):
    # Mengirimkan permintaan POST ke /auth/login untuk mendapatkan token
    response = client.post('/auth/login', json={"email": "user1@example.com", "password": "pass123"})
    
    # Memastikan respons status adalah 200 OK
    assert response.status_code == 200
    
    # Memastikan token akses ada di dalam respons
    assert "access_token" in response.json

# Menguji endpoint /items (publik, tanpa JWT)
def test_get_items(client):
    # Mengirimkan permintaan GET ke /items untuk melihat daftar item marketplace
    response = client.get('/items')
    
    # Memastikan respons status adalah 200 OK
    assert response.status_code == 200
    
    # Memastikan data item ada di dalam respons
    assert "items" in response.json

# Menguji endpoint /profile (terproteksi, dengan JWT)
def test_update_profile(client):
    # Mengirimkan permintaan POST ke /auth/login untuk mendapatkan token
    login_response = client.post('/auth/login', json={"email": "user1@example.com", "password": "pass123"})
    token = login_response.json['access_token']  # Ambil token dari respons login
    
    # Menggunakan token untuk mengakses endpoint PUT /profile dan memperbarui profil
    response = client.put('/profile', json={"name": "Updated Name", "email": "updated@example.com"},
                          headers={"Authorization": f"Bearer {token}"})
    
    # Memastikan respons status adalah 200 OK
    assert response.status_code == 200
    
    # Memastikan nama profil yang diperbarui sesuai
    assert response.json["profile"]["name"] == "Updated Name"
    assert response.json["profile"]["email"] == "updated@example.com"

