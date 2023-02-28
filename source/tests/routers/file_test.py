import os

from fastapi.testclient import TestClient
from pytest import fixture


def test_upload_file(client: TestClient, auth_header: dict) -> None:
    file_path = os.path.join(os.getcwd(), "source", "tests", "misc", "arch.jpg")
    files = [("files", open(file_path, "rb"))]
    res = client.post(
        "/file",
        headers=auth_header,
        files=files,
    )
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


def test_get_owned_files(client, auth_header: dict) -> None:
    res = client.get("/file/owned", headers=auth_header)
    assert res.status_code == 200


def test_get_shared_files(client, auth_header: dict) -> None:
    res = client.get("/file/shared", headers=auth_header)
    assert res.status_code == 200
