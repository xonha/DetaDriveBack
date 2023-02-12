from fastapi.testclient import TestClient

from source import app

client = TestClient(app)


def test_get_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
