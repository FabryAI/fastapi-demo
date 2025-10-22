import uuid
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.main import app
from app.db.database import get_db
from app.core.security import hash_password, create_access_token

client = TestClient(app)


def create_test_user(db, email="report@test.com", password="supersecret"):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, hashed_password=hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_auth_headers(user: User):
    token = create_access_token(data={"sub": user.email})
    return {"Authorization": f"Bearer {token}"}


def test_report_empty_ok():
    db = next(get_db())
    user = create_test_user(db)

    start = datetime.utcnow() - timedelta(days=1)
    end = datetime.utcnow()

    response = client.get(
        "/report",
        params={"datetimeStart": start.isoformat(), "datetimeEnd": end.isoformat()},
        headers=get_auth_headers(user),
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_report_invalid_dates():
    db = next(get_db())
    user = create_test_user(db)

    start = datetime.utcnow()
    end = start - timedelta(days=1)

    response = client.get(
        "/report",
        params={"datetimeStart": start.isoformat(), "datetimeEnd": end.isoformat()},
        headers=get_auth_headers(user),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "end_date must be >= start_date"

