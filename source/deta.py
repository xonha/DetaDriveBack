import os
import deta
import datetime


from source import schemas
from typing import List
from fastapi import UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import HTTPException


deta_key = os.getenv("DETA_PROJECT_KEY")

_deta = deta.Deta(deta_key)  # type: ignore

bkt_storage = _deta.Drive("storage")

tbl_users = _deta.Base("users")
tbl_files = _deta.Base("files")
tbl_users_files = _deta.Base("users_files")


def get_user_by_username(username: str) -> schemas.User:
    try:
        res = tbl_users.fetch({"username": username}).items[0]
        return schemas.User(**res)
    except IndexError:
        raise HTTPException(status_code=404, detail="User not found")


def user_exists(username: str) -> bool:
    try:
        tbl_users.fetch({"username": username}).items[0]
    except IndexError:
        return False
    return True


def insert_user(user: schemas.UserLogin):
    return tbl_users.insert(user.dict())


async def insert_files(files: List[UploadFile], user_key: str):
    res_list: list = []

    for file in files:
        file_bytes = await file.read()
        file_size = len(file_bytes)

        if file_size > 52428800:
            res_list.append(
                {
                    "name": file.filename,
                    "size": file_size,
                    "error": "File size exceeds 50MB",
                }
            )
            continue

        data = schemas.File(
            name=file.filename,
            size=file_size,
            owner_key=user_key,
            content_type=file.content_type,
            last_modified=str(datetime.datetime.now()),
        )

        try:
            res = tbl_files.insert(data=data.dict())
            res_list.append(res)
        except Exception as e:
            res_list.append({"error": str(e)})
            continue
        try:
            bkt_storage.put(
                name=res["key"], data=file_bytes, content_type=file.content_type
            )
        except Exception as e:
            res_list.append({"error": str(e)})
            continue

    return JSONResponse(res_list)


# combination of user_key and file_key must be unique
async def share_file(file_key: str, user_key: str, share_with: str):

    if user_key != tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    if not user_exists(share_with):
        raise HTTPException(status_code=404, detail="User not found")

    try:
        tbl_users_files.insert({"user_key": share_with, "file_key": file_key})
        return {"message": f"File ({file_key}) shared successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def delete_file(file_key: str, user_key: str):
    if user_key != tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    if tbl_files.fetch({"key": file_key}).items[0]["deleted"] == False:
        raise HTTPException(status_code=403, detail="File is not in trash")
    try:
        tbl_files.delete(file_key)
        res = bkt_storage.delete(file_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f'File "{res}" deleted successfully'}


async def update_file(file_key: str, updates: dict, user_key: str):
    if user_key != tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    clean_updates = _remove_none_from_dict(updates)

    update_dict = {"last_modified": str(datetime.datetime.now()), **clean_updates}

    try:
        tbl_files.update(updates=update_dict, key=file_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f'File "{file_key}" updated successfully'}


async def get_files(user_key: str) -> schemas.File:
    try:
        return tbl_files.fetch({"owner_key": user_key, "deleted": False}).items
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def get_file(file_key: str, user_key: str):
    if user_key != tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        return tbl_files.fetch({"key": file_key}).items[0]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def get_trash(user_key: str) -> schemas.File:
    try:
        return tbl_files.fetch({"owner_key": user_key, "deleted": True}).items
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def send_to_trash(file_key: str, user_key: str):
    if user_key != tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        tbl_files.update(updates={"deleted": True}, key=file_key)
        return {"message": f"File ({file_key}) sent to trash successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def restore_file(file_key: str, user_key: str):
    if user_key != tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        tbl_files.update(updates={"deleted": False}, key=file_key)
        return {"message": f"File ({file_key}) restored successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def download_file(file_key: str, user_key: str):
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
