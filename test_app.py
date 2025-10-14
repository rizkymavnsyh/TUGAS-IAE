import pytest
from app import app, db, User
import os


@pytest.fixture(scope="module")
def test_app():
    db_name = os.getenv("DB_NAME", "flask_api")
    test_db_name = f"test_{db_name}"

    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")

    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{test_db_name}",
            "JWT_SECRET": "test-secret",
        }
    )

    with app.app_context():
        db.create_all()

        if not User.query.filter_by(email="user1@example.com").first():
            user1 = User(email="user1@example.com", name="User One", role="user")
            user1.set_password("pass123")
            db.session.add(user1)
            db.session.commit()

    yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(test_app):
    return test_app.test_client()


def test_login(client):
    response = client.post(
        "/auth/login", json={"email": "user1@example.com", "password": "pass123"}
    )

    assert response.status_code == 200
    assert "access_token" in response.json
    assert "refresh_token" in response.json


def test_refresh_token(client):
    login_response = client.post(
        "/auth/login", json={"email": "user1@example.com", "password": "pass123"}
    )
    refresh_token = login_response.json["refresh_token"]

    refresh_response = client.post(
        "/auth/refresh", json={"refresh_token": refresh_token}
    )

    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json


def test_get_items(client):
    response = client.get("/items")

    assert response.status_code == 200
    assert "items" in response.json


def test_update_profile(client):
    login_response = client.post(
        "/auth/login", json={"email": "user1@example.com", "password": "pass123"}
    )
    token = login_response.json["access_token"]

    response = client.put(
        "/profile",
        json={"name": "Updated Name", "email": "updated@example.com"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json["profile"]["name"] == "Updated Name"
    assert response.json["profile"]["email"] == "updated@example.com"


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/login", json={"email": "user1@example.com", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert "error" in response.json
    assert response.json["error"] == "Invalid credentials"
