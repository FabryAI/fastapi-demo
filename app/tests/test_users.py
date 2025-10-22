import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models.user import User
from utils import hash_password

client = TestClient(app)

def random_email(prefix="user"):  # ho introdotto questa poiché fallirebbe su più esecuzioni (di test) dato che l'email deve essere unica
    return f"{prefix}_{uuid.uuid4().hex[:8]}@example.com"

@pytest.fixture(scope="module")
def test_user():
    """Crea un utente di test direttamente nel DB, ritorna (email, password)"""
    db = SessionLocal()
    email = "testuser@example.com"
    password = "testpassword"
    hashed_pw = hash_password(password)

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, hashed_password=hashed_pw)
        db.add(user)
        db.commit()
        db.refresh(user)

    db.close()
    return email, password


@pytest.fixture
def token(test_user):
    """Effettua login e restituisce il token JWT"""
    email, password = test_user
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    return data["access_token"]


def test_create_user(token):
    """Crea un nuovo utente con token valido"""
    payload = {
        "email": random_email("newuser"),
        "password": "supersecret",
    }
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/users", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data


def test_get_user(token):
    """Crea un utente e poi lo recupera"""
    payload = {
        "email": random_email("anotheruser"),
        "password": "anothersecret",
    }
    headers = {"Authorization": f"Bearer {token}"}

    # crea
    res_create = client.post("/users", json=payload, headers=headers)
    assert res_create.status_code == 201, res_create.text
    user_id = res_create.json()["id"]

    # recupera
    res_get = client.get(f"/users/{user_id}", headers=headers)
    assert res_get.status_code == 200, res_get.text
    assert res_get.json()["email"] == payload["email"]
