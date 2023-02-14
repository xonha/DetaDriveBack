from random import randint


def test_register(client) -> None:
    credentials = f"test_{randint(1000, 9999)}"
    res = client.post(
        "/user/register", json={"username": credentials, "password": credentials}
    )
    assert res.status_code == 201
    assert res.json()["message"] == "User created successfully"


def test_login(client) -> None:
    res = client.post("/user/login", json={"username": "string", "password": "string"})
    assert res.status_code == 200
    assert res.json()["type"] == "Bearer"


def test_get_users(client) -> None:
    res = client.get("/user")
    assert res.status_code == 200
