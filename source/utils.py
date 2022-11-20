from fastapi import HTTPException, Request

from source import db, schemas


def remove_none_values_from_dict(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def get_user_by_username(username: str) -> schemas.User:
    try:
        res = db.tbl_users.fetch({"username": username}).items[0]
        return schemas.User(**res)
    except IndexError:
        raise HTTPException(status_code=404, detail="User not found")


def username_exists(username: str) -> bool:
    try:
        db.tbl_users.fetch({"username": username}).items[0]
    except IndexError:
        return False
    return True


def user_key_exists(key: str) -> bool:
    try:
        db.tbl_users.fetch({"key": key}).items[0]
    except IndexError:
        return False
    return True


def get_user_credentials_from_state(req: Request) -> schemas.User:
    user_credentials: dict = req.get("state")["user_credentials"]  # type: ignore
    return schemas.User(**user_credentials)


def user_owns_file(user_key: str, file_key: str) -> bool:
    try:
        res = db.tbl_files.fetch({"key": file_key}).items[0]
        if res["owner_key"] == user_key:
            return True
        return False
    except IndexError:
        raise HTTPException(status_code=404, detail="File not found")


def user_has_access_to_file(user_key: str, file_key: str) -> bool:
    query = {"user_key": user_key, "file_key": file_key}
    try:
        res = db.tbl_users_files.fetch(query).items[0]
        if res:
            return True
        return False
    except IndexError:
        raise HTTPException(status_code=404, detail="File not found")
