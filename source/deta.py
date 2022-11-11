import datetime
from typing import List

from fastapi import Request, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

from source import auth, db, schemas, utils

_auth = auth.AuthHandler()


async def register(user: schemas.UserLogin):
    if utils.user_exists(user.username):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = _auth.get_password_hash(user.password)
    user_to_insert = schemas.UserLogin(username=user.username, password=hashed_password)

    try:
        db.tbl_users.insert(user_to_insert.dict())
        return {"message": "User created successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def login(user: schemas.UserLogin):
    exception_detail = "Incorrect username or password"

    db_user = utils.get_user_by_username(user.username)
    if not db_user:
        raise HTTPException(status_code=404, detail=exception_detail)

    password_verified = _auth.verify_password(user.password, db_user.password)
    if not password_verified:
        raise HTTPException(status_code=404, detail=exception_detail)

    return {"type": "Bearer", "token": _auth.encode_token(db_user.dict())}


async def upload_files(req: Request, files: List[UploadFile]):
    user = utils.get_user_credentials_from_state(req)
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
            owner_key=user.key,
            content_type=file.content_type,
            last_modified=str(datetime.datetime.now()),
        )

        try:
            res = db.tbl_files.insert(data=data.dict())
            res_list.append(res)
        except Exception as e:
            res_list.append({"error": str(e)})
            continue
        try:
            db.storage.put(
                name=res["key"], data=file_bytes, content_type=file.content_type
            )
        except Exception as e:
            res_list.append({"error": str(e)})
            continue

    return JSONResponse(res_list)


async def share_file(req: Request, file_key: str, share_with: str):
    user = utils.get_user_credentials_from_state(req)

    if user.key != db.tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    if not utils.user_exists(share_with):
        raise HTTPException(status_code=404, detail="User not found")

    try:
        db.tbl_users_files.insert({"user_key": share_with, "file_key": file_key})
        return {"message": f"File ({file_key}) shared successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def update_file(req: Request, file_key: str, updates: dict):
    user = utils.get_user_credentials_from_state(req)

    if user.key != db.tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    clean_updates = utils.remove_none_values_from_dict(updates)

    update_dict = {"last_modified": str(datetime.datetime.now()), **clean_updates}

    try:
        db.tbl_files.update(updates=update_dict, key=file_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f'File "{file_key}" updated successfully'}


async def send_to_trash(req: Request, file_key: str):
    user = utils.get_user_credentials_from_state(req)

    if user.key != db.tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        db.tbl_files.update(updates={"deleted": True}, key=file_key)
        return {"message": f"File ({file_key}) sent to trash successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def get_file(req: Request, file_key: str):
    user = utils.get_user_credentials_from_state(req)

    if user.key != db.tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        return db.tbl_files.fetch({"key": file_key}).items[0]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def download_file(req: Request, file_key: str):
    user = utils.get_user_credentials_from_state(req)

    if user.key != db.tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        file = db.tbl_files.fetch({"key": file_key}).items[0]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    try:
        res = db.storage.get(file_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return StreamingResponse(
        content=res.iter_chunks(1024),
        media_type=file["content_type"],
        headers={"Content-Disposition": f"attachment; filename={file['name']}"},
    )


async def get_files(req: Request) -> schemas.File:
    user = utils.get_user_credentials_from_state(req)

    try:
        return db.tbl_files.fetch({"owner_key": user.key, "deleted": False}).items
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def get_trash(req: Request) -> schemas.File:
    user = utils.get_user_credentials_from_state(req)

    try:
        return db.tbl_files.fetch({"owner_key": user.key, "deleted": True}).items
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def restore_file(req: Request, file_key: str):
    user = utils.get_user_credentials_from_state(req)

    if user.key != db.tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    try:
        db.tbl_files.update(updates={"deleted": False}, key=file_key)
        return {"message": f"File ({file_key}) restored successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def delete_file(req: Request, file_key: str):
    user = utils.get_user_credentials_from_state(req)

    if user.key != db.tbl_files.fetch({"key": file_key}).items[0]["owner_key"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    if db.tbl_files.fetch({"key": file_key}).items[0]["deleted"] == False:
        raise HTTPException(status_code=403, detail="File is not in trash")
    try:
        db.tbl_files.delete(file_key)
        res = db.storage.delete(file_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f'File "{res}" deleted successfully'}
