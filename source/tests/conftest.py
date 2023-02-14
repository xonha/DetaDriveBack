from fastapi.testclient import TestClient
from pytest import fixture

from source import app


@fixture
def client() -> TestClient:
    return TestClient(app)


@fixture
def auth_header(client):
    res = client.post("/user/login", json={"username": "string", "password": "string"})
    access_token = res.json()["token"]
    return {"Authorization": f"Bearer {access_token}"}
