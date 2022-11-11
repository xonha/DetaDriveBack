from fastapi import Request

from source import db, schemas


def remove_none_values_from_dict(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}


def get_user_by_username(username: str) -> schemas.User:
    try:
        res = db.tbl_users.fetch({"username": username}).items[0]
        return schemas.User(**res)
    except Exception as e:
        raise e


def user_exists(username: str) -> bool:
    try:
        db.tbl_users.fetch({"username": username}).items[0]
    except IndexError:
        return False
    return True


def get_user_credentials_from_state(req: Request) -> schemas.User:
    user_credentials: dict = req.get("state")["user_credentials"]  # type: ignore
    return schemas.User(**user_credentials)
