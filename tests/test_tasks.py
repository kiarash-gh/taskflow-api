
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.main import app, get_db
from app import models


@pytest.fixture
def client():
    # Create a separate in-memory database for testing.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestSessionLocal = sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


def test_create_task(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Learn testing",
            "description": "Write my first API test",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Learn testing"
    assert data["description"] == "Write my first API test"
    assert data["completed"] is False
    assert isinstance(data["id"], int)


def test_list_tasks(client):
    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B"})

    response = client.get("/tasks")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "Task A"


def test_get_missing_task(client):
    response = client.get("/tasks/99999")

    assert response.status_code == 404


def test_update_task(client):
    created = client.post(
        "/tasks",
        json={"title": "Original title"},
    )
    task_id = created.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"completed": True},
    )

    assert response.status_code == 200
    assert response.json()["completed"] is True
    assert response.json()["title"] == "Original title"


def test_delete_task(client):
    created = client.post(
        "/tasks",
        json={"title": "Task to delete"},
    )
    task_id = created.json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_create_task_rejects_long_title(client):
    response = client.post(
        "/tasks",
        json={"title": "A" * 201},
    )

    assert response.status_code == 422


def test_create_task_with_priority(client):
    response = client.post(
        "/tasks",
        json={
            "title": "High priority task",
            "priority": 1,
        },
    )

    assert response.status_code == 201
    assert response.json()["priority"] == 1


def test_create_task_rejects_invalid_priority(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Invalid priority",
            "priority": 5,
        },
    )

    assert response.status_code == 422
