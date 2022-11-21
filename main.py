from typing import List

from fastapi import Depends, FastAPI, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from source import deta, schemas
from source.auth import AuthHandler

app = FastAPI()
auth = AuthHandler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.post("/register", status_code=201, tags=["Auth"])
async def register(user: schemas.UserLogin):
    return await deta.register(user)


@app.post("/login", tags=["Auth"])
async def login(user: schemas.UserLogin):
    return await deta.login(user)


@app.get("/users", tags=["Auth"])
async def get_users():
    return await deta.get_users()


@app.post("/file", tags=["Storage"])
async def upload_files(
    req: Request,
    files: List[UploadFile],
    auth=Depends(auth.auth_middleware),
):
    return await deta.upload_files(req, files)


@app.post("/file/{file_key}/share ", tags=["Storage"])
async def share_file(
    req: Request,
    file_key: str,
    share_with: str,
    auth=Depends(auth.auth_middleware),
):
    return await deta.share_file(req, file_key, share_with)


@app.patch("/file/{file_key}/rename", tags=["Storage"])
async def rename_file(
    req: Request,
    file_key: str,
    body: schemas.BodyRename,
    auth=Depends(auth.auth_middleware),
):
    return await deta.rename_file(req, file_key, body.name)


@app.patch("/file/{file_key}/change_owner", tags=["Storage"])
async def change_owner(
    req: Request,
    file_key: str,
    body: schemas.BodyChangeOwner,
    auth=Depends(auth.auth_middleware),
):
    return await deta.change_owner(req, file_key, body.owner_key)


@app.patch("/file/{file_key}/send_to_trash", tags=["Storage"])
async def send_to_trash(
    req: Request, file_key: str, auth=Depends(auth.auth_middleware)
):
    return await deta.send_to_trash(req, file_key)


@app.delete("/file/{file_key}/stop_seeing", tags=["Storage"])
async def stop_seeing(req: Request, file_key: str, auth=Depends(auth.auth_middleware)):
    return await deta.stop_seeing(req, file_key)


@app.get("/file/{file_key}", tags=["Storage"])
async def get_file(req: Request, file_key: str, auth=Depends(auth.auth_middleware)):
    return await deta.get_file(req, file_key)


@app.get("/file/{file_key}/download", tags=["Storage"])
async def download_file(
    req: Request, file_key: str, auth=Depends(auth.auth_middleware)
):
    return await deta.download_file(req, file_key)


@app.get("/files/owned", tags=["Storage"])
async def get_owned_files(req: Request, auth=Depends(auth.auth_middleware)):
    return await deta.get_owned_files(req)


@app.get("/files/shared", tags=["Storage"])
async def get_shared_files(req: Request, auth=Depends(auth.auth_middleware)):
    return await deta.get_shared_files(req)


@app.get("/trash", tags=["Trash"])
async def get_trash(req: Request, auth=Depends(auth.auth_middleware)):
    return await deta.get_trash(req)


@app.patch("/trash/{file_key}", tags=["Trash"])
async def restore_file(req: Request, file_key: str, auth=Depends(auth.auth_middleware)):
    return await deta.restore_file(req, file_key)


@app.delete("/trash/{file_key}", tags=["Trash"])
async def delete_file(req: Request, file_key: str, auth=Depends(auth.auth_middleware)):
    return await deta.delete_file(req, file_key)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
