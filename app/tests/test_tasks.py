import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.models.user import User
from app.models.project import Project
from app.models.task import Task as TaskModel
from app.main import app
from app.db.database import get_db
from app.core.security import hash_password, create_access_token

client = TestClient(app)


# Helpers ------------------------------------------------------------------

def create_test_user(db, email="tasks@test.com", password="supersecret"):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, hashed_password=hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def create_test_project(db):
    project = Project(name="Project for tasks") 
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def auth_headers(user: User):
    token = create_access_token(data={"sub": user.email})
    return {"Authorization": f"Bearer {token}"}


# Tests --------------------------------------------------------------------

def test_create_and_get_task():
    db = next(get_db())
    user = create_test_user(db)
    project = create_test_project(db)

    payload = {
        "project": str(project.id),
        "user": str(user.id),
        "activity": "Test Task",
        "datetimeStart": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
        "datetimeEnd": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
    }

    # Create
    response = client.post("/tasks", json=payload, headers=auth_headers(user))
    assert response.status_code == 201
    data = response.json()
    assert data["activity"] == "Test Task"

    task_id = data["id"]

    # Get by id
    res2 = client.get(f"tasks/{task_id}", headers=auth_headers(user))
    assert res2.status_code == 200
    assert res2.json()["id"] == task_id


def test_update_task():
    db = next(get_db())
    user = create_test_user(db)
    project = create_test_project(db)  

    # creo un task diretto su DB
    task = TaskModel(
        project_id=project.id,
        user_id=user.id,
        activity="Old Task",
        start_time=datetime.utcnow() - timedelta(hours=3),
        end_time=datetime.utcnow() - timedelta(hours=2),
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    payload = {
        "project": str(project.id),
        "user": str(user.id),
        "activity": "Updated Task",
        "datetimeStart": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
        "datetimeEnd": datetime.utcnow().isoformat(),
    }

    response = client.put(f"/tasks/{task.id}", json=payload, headers=auth_headers(user))
    assert response.status_code == 200
    assert response.json()["activity"] == "Updated Task"


def test_delete_task():
    db = next(get_db())
    user = create_test_user(db)
    project = create_test_project(db)

    task = TaskModel(
        project_id=project.id,
        user_id=user.id,
        activity="Delete Me",
        start_time=datetime.utcnow() - timedelta(hours=1),
        end_time=datetime.utcnow(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    response = client.delete(f"/tasks/{task.id}", headers=auth_headers(user))
    assert response.status_code == 204

    # verify deletion
    res2 = client.get(f"/{task.id}", headers=auth_headers(user))
    assert res2.status_code == 404
