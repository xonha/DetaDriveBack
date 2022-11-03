if __name__ == "__main__":
    import deta

    deta = deta.Deta("e0b2v1gk_DA4wfBpEdUbJAQnJWURfRWc3YQ9zZ3jD")
    u = deta.Base("users")
    f = deta.Base("files")
    uf = deta.Base("users_files")


    user = u.insert(
        {
            "username": "John Doe",
            "password": "123456",
        }
    )

    file = f.insert(
        {
            "name": "file",
            "type": "txt",
            "size": 14.7,
            "owner_key": user["key"],
            "last_modified": "2021-08-01T00:00:00",
        }
    )

    uf.insert(
        {
            "user_key": user["key"],
            "file_key": file["key"],
        }
    )

    print("Starting Deta micro")
