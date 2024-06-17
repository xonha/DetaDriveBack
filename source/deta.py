import datetime
from typing import List

from fastapi import Request, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse, StreamingResponse

from source import auth, db, schemas, utils

_auth = auth.AuthHandler()


async def register(user: schemas.UserLogin):
    if utils.username_exists(user.username):
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


async def get_users():
    try:
        users = db.tbl_users.fetch().items
        users_without_password = map(
            lambda user: {
                key: value for key, value in user.items() if key != "password"
            },
            users,
        )
        return list(users_without_password)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


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

    relation = schemas.UserFileRelation(
        owner_key=user.key,
        user_key=share_with,
        file_key=file_key,
    )
    if not utils.user_key_exists(share_with):
        raise HTTPException(status_code=404, detail="User not found")

    relation_exists = db.tbl_users_files.fetch(relation.dict())
    if relation_exists.items:
        return {"message": "Suceessfully shared file"}

    if not utils.user_owns_file(user.key, file_key):
        raise HTTPException(status_code=403, detail="File does not belong to user")

    try:
        db.tbl_users_files.insert(relation.dict())
        return {"message": "Suceessfully shared file"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def rename_file(req: Request, file_key: str, new_file_name: str):
    user = utils.get_user_credentials_from_state(req)

    if not utils.user_owns_file(user.key, file_key):
        raise HTTPException(status_code=403, detail="File does not belong to user")

    update_dict = {"name": new_file_name, "last_modified": str(datetime.datetime.now())}

    try:
        db.tbl_files.update(updates=update_dict, key=file_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": "File renamed successfully"}


async def change_owner(req: Request, file_key: str, new_owner: str):
    user = utils.get_user_credentials_from_state(req)

    if not utils.user_owns_file(user.key, file_key):
        raise HTTPException(status_code=403, detail="File does not belong to user")
    if not utils.user_key_exists(new_owner):
        raise HTTPException(status_code=404, detail="New owner not found")

    files = db.tbl_users_files.fetch(
        {"file_key": file_key, "owner_key": user.key, "user_key": new_owner}
    )

    if len(files.items) == 0:
        try:
            db.tbl_users_files.insert(
                {
                    "owner_key": new_owner,
                    "user_key": user.key,
                    "file_key": file_key,
                }
            )
            db.tbl_files.update(updates={"owner_key": new_owner}, key=file_key)
            return {"message": "File owner changed successfully"}
        except Exception as e:
            raise HTTPException(status_code=404, detail=str(e))

    file = files.items[0]
    try:
        db.tbl_users_files.update(
            key=file["key"], updates={"owner_key": new_owner, "user_key": user.key}
        )
        db.tbl_files.update(updates={"owner_key": new_owner}, key=file_key)
        return {"message": f"File ({file_key}) owner changed successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def send_to_trash(req: Request, file_key: str):
    user = utils.get_user_credentials_from_state(req)

    if not utils.user_owns_file(user.key, file_key):
        raise HTTPException(status_code=403, detail="File does not belong to user")
    try:
        db.tbl_files.update(updates={"deleted": True}, key=file_key)
        return {"message": f"File ({file_key}) sent to trash successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def stop_seeing(req: Request, file_key: str):
    user = utils.get_user_credentials_from_state(req)

    if not utils.user_has_access_to_file(user.key, file_key):
        raise HTTPException(status_code=403, detail="User does not have access to file")
    try:
        db.tbl_users_files.delete(user_key=user.key, file_key=file_key)
        return {"message": f"User ({user.key}) stopped seeing file ({file_key})"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def get_file(req: Request, file_key: str):
    user = utils.get_user_credentials_from_state(req)

    if not utils.user_owns_file(user.key, file_key):
        raise HTTPException(status_code=403, detail="File does not belong to user")
    try:
        return db.tbl_files.fetch({"key": file_key}).items[0]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def download_file(req: Request, file_key: str):
    user = utils.get_user_credentials_from_state(req)
    print("user", user)

    user_owns_file = utils.user_owns_file(user.key, file_key)
    user_has_access_to_file = utils.user_has_access_to_file(user.key, file_key)

    if not user_owns_file or user_has_access_to_file:
        raise HTTPException(status_code=403, detail="User does not have access to file")

    try:
        file = db.tbl_files.fetch({"key": file_key}).items[0]
        print(file)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    try:
        res = db.storage.get(file_key)
        print(res)
        return StreamingResponse(
            content=res.iter_chunks(1024),
            media_type=file["content_type"],
            headers={"Content-Disposition": f"attachment; filename={file['name']}"},
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def get_owned_files(req: Request) -> schemas.File:
    user = utils.get_user_credentials_from_state(req)
    try:
        return db.tbl_files.fetch({"owner_key": user.key, "deleted": False}).items
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def get_shared_files(req: Request) -> list:
    user = utils.get_user_credentials_from_state(req)
    try:
        items_shared = db.tbl_users_files.fetch({"user_key": user.key}).items
        file_keys = [item["file_key"] for item in items_shared]
        items = map(lambda key: db.tbl_files.fetch({"key": key}).items[0], file_keys)
        return list(items)
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

    if not utils.user_owns_file(user.key, file_key):
        raise HTTPException(status_code=403, detail="File does not belong to user")
    try:
        db.tbl_files.update(updates={"deleted": False}, key=file_key)
        return {"message": f"File ({file_key}) restored successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


async def delete_file(req: Request, file_key: str):
    user = utils.get_user_credentials_from_state(req)

    if not utils.user_owns_file(user.key, file_key):
        raise HTTPException(status_code=403, detail="File does not belong to user")

    if db.tbl_files.fetch({"key": file_key}).items[0]["deleted"] == False:
        raise HTTPException(status_code=403, detail="File is not in trash")
    try:
        db.tbl_files.delete(file_key)
        res = db.storage.delete(file_key)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": f'File "{res}" deleted successfully'}
