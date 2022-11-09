import os
import deta
import datetime

from src import schemas
from fastapi import UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import HTTPException


deta_key = os.getenv("DETA_PROJECT_KEY")

_deta = deta.Deta(deta_key)

bkt_storage = _deta.Drive("storage")

tbl_users = _deta.Base("users")
tbl_files = _deta.Base("files")
tbl_users_files = _deta.Base("users_files")


def get_user_by_username(username: str) -> schemas.User:
    return tbl_users.fetch({"username": username}).items[0]


def insert_user(user: schemas.UserLogin):
    return tbl_users.insert(user)


async def insert_file(file: UploadFile, user_key: str):
    file_bytes = await file.read()
    file_size = len(file_bytes)

    if file_size > 52428800:
        raise HTTPException(status_code=400, detail="File size is too large")

    data = {
        "name": file.filename,
        "size": file_size,
        "owner_key": user_key,
        "content_type": file.content_type,
        "last_modified": str(datetime.datetime.now()),
    }
    try:
        res_base = tbl_files.insert(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    try:
        bkt_storage.put(
            name=res_base["key"], data=file_bytes, content_type=file.content_type
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    return JSONResponse(res_base)


async def delete_file(file_key: str, user_key: str) -> schemas.Record:
    if user_key != tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        tbl_files.delete(file_key)
        res = bkt_storage.delete(file_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f'File "{res}" deleted successfully'}


async def update_file(file_key: str, updates: dict, user_key: str) -> schemas.Record:
    if user_key != tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    clean_updates = _remove_none_from_dict(updates)

    update_dict = {"last_modified": str(datetime.datetime.now()), **clean_updates}

    try:
        tbl_files.update(updates=update_dict, key=file_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f'File "{file_key}" updated successfully'}


async def list_all_files(user_key: str) -> schemas.File:
    try:
        res = tbl_files.fetch({"owner_key": user_key}).items
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return res


async def download_file(file_key: str, user_key: str) -> schemas.Record:
    if user_key != tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        file = tbl_files.fetch({"key": file_key}).items[0]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    try:
        res = bkt_storage.get(file_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return StreamingResponse(
        content=res.iter_chunks(1024),
        media_type=file["content_type"],
        headers={"Content-Disposition": f"attachment; filename={file['name']}"},
    )


def _remove_none_from_dict(d: dict) -> dict:
    return {k: v for k, v in d.items() if v is not None}
