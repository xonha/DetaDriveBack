from random import randint

from fastapi.testclient import TestClient
from pytest import Cache, mark


@mark.dependency()
def test_register_user(client: TestClient, cache: Cache) -> None:
    credential = f"test_{randint(1000, 9999)}"

    res = client.post(
        "/user/register", json={"username": credential, "password": credential}
    )
    res_json = res.json()

    assert res.status_code == 201
    assert res_json["message"] == "User created successfully"
    cache.set(f"registred_user", credential)


@mark.dependency(depends=["test_register_user"])
def test_login_user(client: TestClient, cache: Cache) -> None:
    credential = cache.get("registred_user", None)
    res = client.post(
        "/user/login", json={"username": credential, "password": credential}
    )

    assert res.status_code == 200
    assert res.json()["type"] == "Bearer"


def test_get_users(client: TestClient) -> None:
    res = client.get("/user")
    assert res.status_code == 200
