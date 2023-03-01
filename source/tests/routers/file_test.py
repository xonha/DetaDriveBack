import os

from fastapi.testclient import TestClient
from pytest import Cache, mark


@mark.dependency(depends=["routers/user_test.py::test_register_user"])
def test_upload_file(client: TestClient, auth_header: dict, cache: Cache) -> None:
    file_path = os.path.join(os.getcwd(), "source", "tests", "misc", "arch.jpg")
    files = [("files", open(file_path, "rb"))]
    res = client.post(
        "/file",
        headers=auth_header,
        files=files,
    )
    res_json = res.json()
    cache.set("file_key", res_json[0]["key"])
    assert res.status_code == 201


def test_upload_files(client: TestClient, auth_header: dict) -> None:
    file1_path = os.path.join(os.getcwd(), "source", "tests", "misc", "arch.jpg")
    file2_path = os.path.join(os.getcwd(), "source", "tests", "misc", "cor.png")
    files = [("files", open(file1_path, "rb")), ("files", open(file2_path, "rb"))]
    res = client.post(
        "/file",
        headers=auth_header,
        files=files,
    )
    assert res.status_code == 201


@mark.dependency(depends=["test_upload_file"])
def test_share_file(client: TestClient, auth_header: dict, cache: Cache):
    file_key = cache.get("file_key", None)
    registred_user = cache.get("registred_user", None)

    assert file_key and registred_user is not None

    res = client.post(
        f"/file/{file_key}/share",
        headers=auth_header,
        json={"share_with": registred_user},
    )
    assert res.status_code == 200


def test_get_owned_files(client, auth_header: dict) -> None:
    res = client.get("/file/owned", headers=auth_header)
    assert res.status_code == 200


def test_get_shared_files(client, auth_header: dict) -> None:
    res = client.get("/file/shared", headers=auth_header)
    assert res.status_code == 200
