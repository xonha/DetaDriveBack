from os import environ

from fastapi.testclient import TestClient
from pytest import fixture

from source import app


@fixture
def client() -> TestClient:
    return TestClient(app)


@fixture
def auth_header(client: TestClient) -> dict:
    password = environ.get("DETA_PROJECT_KEY")
    res = client.post("/user/login", json={"username": "admin", "password": password})
    access_token = res.json()["token"]
    return {"Authorization": f"Bearer {access_token}"}
