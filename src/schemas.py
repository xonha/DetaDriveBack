from pydantic import BaseModel


class User(BaseModel):
    username: str
    password: str


class File(BaseModel):
    name: str
    size: float
    owner_key: str
    last_modified: str


class UserFile(BaseModel):
    user_key: str
    file_key: str
