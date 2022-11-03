import os
import deta

from src import schemas


class DetaHelper:
    def __init__(self):
        self._deta = deta.Deta(os.getenv("DETA_PROJECT_KEY"))
        self._users = self._deta.Base("users")
        self._files = self._deta.Base("files")
        self._users_files = self._deta.Base("users_files")

    def get_users_list(self) -> list:
        return list(map(lambda x: x["username"], self._users.fetch().items))

    def get_users_dict(self) -> dict:
        return {x["username"]: x["key"] for x in self._users.fetch().items}

    def insert_user(self, user: schemas.User):
        return self._users.insert(user)

    def get_hashed_password(self, user_key: str) -> str:
        return self._users.get(user_key)["password"]
