def test_upload_file(client, auth_header) -> None:
    res = client.post(
        "/file/upload",
        headers=auth_header,
        files={"file": ("test.txt", b"some text data")},
    )
    assert res.status_code == 201


def test_get_owned_files(client, auth_header) -> None:
    res = client.get("/file/owned", headers=auth_header)
    assert res.status_code == 200


def test_get_shared_files(client, auth_header) -> None:
    res = client.get("/file/shared", headers=auth_header)
    assert res.status_code == 200
