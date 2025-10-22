import uuid
from fastapi.testclient import TestClient
from app.models.user import User
from app.models.project import Project
from app.main import app
from app.db.database import get_db
from app.core.security import hash_password, create_access_token

client = TestClient(app)


# Helpers ------------------------------------------------------------------

def create_test_user(db, email="projects@test.com", password="supersecret"):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, hashed_password=hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def auth_headers(user: User):
    token = create_access_token(data={"sub": user.email})
    return {"Authorization": f"Bearer {token}"}


# Tests --------------------------------------------------------------------

def test_create_project():
    db = next(get_db())
    user = create_test_user(db)

    payload = {"name": "My Test Project"}
    response = client.post("/projects", json=payload, headers=auth_headers(user))

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Test Project"
    assert "id" in data


def test_list_projects():
    db = next(get_db())
    user = create_test_user(db)

    response = client.get("/projects", headers=auth_headers(user))
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_project_not_found():
    db = next(get_db())
    user = create_test_user(db)

    # ID casuale che non esiste
    random_id = str(uuid.uuid4())
    response = client.get(f"/projects/{random_id}", headers=auth_headers(user))

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_get_project_success():
    db = next(get_db())
    user = create_test_user(db)

    # Creo progetto manualmente
    project = Project(name="Project Get")
    db.add(project)
    db.commit()
    db.refresh(project)

    response = client.get(f"/projects/{project.id}", headers=auth_headers(user))
    assert response.status_code == 200
    assert response.json()["id"] == str(project.id)
    assert response.json()["name"] == "Project Get"
