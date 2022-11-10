from typing import List
from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse


from source.auth import AuthHandler
from source import schemas, deta


app = FastAPI()
auth = AuthHandler()


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.post("/register", status_code=201, tags=["Auth"])
async def register(user: schemas.UserLogin):
    if deta.user_exists(user.username):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = auth.get_password_hash(user.password)
    user_to_insert = schemas.UserLogin(username=user.username, password=hashed_password)

    deta.insert_user(user_to_insert)

    return {"message": f"User {user.username} created successfully"}


@app.post("/login", tags=["Auth"])
async def login(user: schemas.UserLogin):
    exception_detail = "Incorrect username or password"

    db_user = deta.get_user_by_username(user.username)
    if not db_user:
        raise HTTPException(status_code=404, detail=exception_detail)

    password_verified = auth.verify_password(user.password, db_user.password)
    if not password_verified:
        raise HTTPException(status_code=404, detail=exception_detail)

    return {"type": "Bearer", "token": auth.encode_token(db_user.dict())}


@app.post("/file", tags=["Storage"])
async def upload_files(
    request: Request,
    files: List[UploadFile],
    auth=Depends(auth.auth_middleware),
):
    return await deta.insert_files(files, request)


@app.post("/file/{file_key}/share ", tags=["Storage"])
async def share_file(
    request: Request,
    file_key: str,
    share_with: str,
    auth=Depends(auth.auth_middleware),
):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.share_file(
        file_key=file_key, share_with=share_with, user_key=payload["key"]
    )


@app.patch("/file/{file_key}", tags=["Storage"])
async def update_file(
    file_key: str,
    data: schemas.FileUpdate,
    request: Request,
    auth=Depends(auth.auth_middleware),
):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.update_file(
        file_key=file_key, updates=dict(data), user_key=payload["key"]
    )


@app.delete("/file/{file_key}", tags=["Storage"])
async def send_to_trash(
    file_key: str, request: Request, auth=Depends(auth.auth_middleware)
):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.send_to_trash(file_key=file_key, user_key=payload["key"])


@app.get("/file/{file_key}", tags=["Storage"])
async def get_file(file_key: str, request: Request, auth=Depends(auth.auth_middleware)):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.get_file(file_key=file_key, user_key=payload["key"])


@app.get("/file/{file_key}/download", tags=["Storage"])
async def download_file(
    file_key: str, request: Request, auth=Depends(auth.auth_middleware)
):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.download_file(file_key=file_key, user_key=payload["key"])


@app.get("/files", tags=["Storage"])
async def get_files(request: Request, auth=Depends(auth.auth_middleware)):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.get_files(user_key=payload["key"])


@app.get("/trash", tags=["Trash"])
async def get_trash(request: Request, auth=Depends(auth.auth_middleware)):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.get_trash(user_key=payload["key"])


@app.patch("/trash/{file_key}", tags=["Trash"])
async def restore_file(
    file_key: str, request: Request, auth=Depends(auth.auth_middleware)
):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.restore_file(file_key=file_key, user_key=payload["key"])


@app.delete("/trash/{file_key}", tags=["Trash"])
async def delete_file(
    file_key: str, request: Request, auth=Depends(auth.auth_middleware)
):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.delete_file(file_key=file_key, user_key=payload["key"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
