import os

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    database_url = os.environ["TEST_DATABASE_URL"]
    with TestClient(create_app(database_url)) as test_client:
        yield test_client


def test_task_crud_persists_data_in_postgresql(client: TestClient) -> None:
    created = client.post(
        "/tasks", json={"title": "  Entregar atividade  ", "description": "Workflow CI"}
    )
    assert created.status_code == 201
    task = created.json()
    assert task["title"] == "Entregar atividade"
    assert task["completed"] is False

    task_id = task["id"]
    fetched = client.get(f"/tasks/{task_id}")
    assert fetched.status_code == 200
    assert fetched.json()["description"] == "Workflow CI"

    updated = client.patch(f"/tasks/{task_id}", json={"completed": True})
    assert updated.status_code == 200
    assert updated.json()["completed"] is True

    listed = client.get("/tasks")
    assert any(item["id"] == task_id for item in listed.json())

    deleted = client.delete(f"/tasks/{task_id}")
    assert deleted.status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_api_rejects_blank_task_title(client: TestClient) -> None:
    response = client.post("/tasks", json={"title": "   "})

    assert response.status_code == 422
