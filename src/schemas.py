from pydantic import BaseModel
from typing import Optional


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserLogin):
    key: Optional[str] = None


class UserFile(BaseModel):
    key: Optional[str] = None
    user_key: str
    file_key: str


class File(BaseModel):
    name: str
    size: int
    owner_key: str
    content_type: str
    last_modified: str


class FileUpdate(BaseModel):
    name: str
    owner_key: str


class Record(BaseModel):
    name: str
    data: bytes
    type: str
