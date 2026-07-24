from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_tasks_endpoint():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_task_endpoint():
    response = client.post("/tasks", json={"title": "Learn GitHub deployment"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Learn GitHub deployment"
    assert data["done"] is False
