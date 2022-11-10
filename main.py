from typing import List
from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse


from src.auth import AuthHandler
from src import schemas, deta


app = FastAPI()
auth_handler = AuthHandler()


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.post("/register", status_code=201, tags=["Auth"])
async def register(user: schemas.UserLogin):
    if deta.user_exists(user.username):
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = auth_handler.get_password_hash(user.password)
    user_to_insert = schemas.User(username=user.username, password=hashed_password)
    deta.insert_user(user_to_insert)

    return {"message": f"User {user.username} created successfully"}


@app.post("/login", tags=["Auth"])
async def login(user: schemas.UserLogin):
    db_user = deta.get_user_by_username(user.username)
    exception_detail = "Incorrect username or password"
    if not user:
        raise HTTPException(status_code=404, detail=exception_detail)
    password_verified = auth_handler.verify_password(user.password, db_user.password)
    if not password_verified:
        raise HTTPException(status_code=404, detail=exception_detail)
    return {
        "token": auth_handler.encode_token(
            {"key": db_user.key, "username": db_user.password}
        ),
        "type": "bearer",
    }


@app.post("/file", tags=["Storage"])
async def upload_file(
    request: Request, files: List[UploadFile], auth=Depends(auth_handler.auth_middleware)
):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.insert_file(files=files, user_key=payload["key"])


@app.patch("/file/{file_key}", tags=["Storage"])
async def update_file(
    file_key: str,
    data: schemas.FileUpdate,
    request: Request,
    auth=Depends(auth_handler.auth_middleware),
):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.update_file(
        file_key=file_key, updates=dict(data), user_key=payload["key"]
    )


@app.delete("/file/{file_key}", tags=["Storage"])
async def send_to_trash(
    file_key: str, request: Request, auth=Depends(auth_handler.auth_middleware)
):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.send_to_trash(file_key=file_key, user_key=payload["key"])


@app.get("/file/{file_key}", tags=["Storage"])
async def get_file(
    file_key: str, request: Request, auth=Depends(auth_handler.auth_middleware)
):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.get_file(file_key=file_key, user_key=payload["key"])


@app.get("/file/{file_key}/download", tags=["Storage"])
async def download_file(
    file_key: str, request: Request, auth=Depends(auth_handler.auth_middleware)
):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.download_file(file_key=file_key, user_key=payload["key"])


@app.get("/files", tags=["Storage"])
async def get_files(request: Request, auth=Depends(auth_handler.auth_middleware)):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.get_files(user_key=payload["key"])


@app.get("/trash", tags=["Trash"])
async def get_trash(request: Request, auth=Depends(auth_handler.auth_middleware)):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.get_trash(user_key=payload["key"])


@app.patch("/trash/{file_key}", tags=["Trash"])
async def restore_file(
    file_key: str, request: Request, auth=Depends(auth_handler.auth_middleware)
):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.restore_file(file_key=file_key, user_key=payload["key"])


@app.delete("/trash/{file_key}", tags=["Trash"])
async def delete_file(
    file_key: str, request: Request, auth=Depends(auth_handler.auth_middleware)
):
    payload = request.get("state")["payload"]  # type: ignore
    return await deta.delete_file(file_key=file_key, user_key=payload["key"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
