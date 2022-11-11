from typing import List

from fastapi import Depends, FastAPI, Request, UploadFile
from fastapi.responses import RedirectResponse

from source import deta, schemas
from source.auth import AuthHandler

app = FastAPI()
auth = AuthHandler()


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.post("/register", status_code=201, tags=["Auth"])
async def register(user: schemas.UserLogin):
    return await deta.register(user)


@app.post("/login", tags=["Auth"])
async def login(user: schemas.UserLogin):
    return await deta.login(user)


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


@app.patch("/file/{file_key}", tags=["Storage"])
async def update_file(
    req: Request,
    file_key: str,
    data: schemas.FileUpdate,
    auth=Depends(auth.auth_middleware),
):
    return await deta.update_file(req, file_key, data.dict())


@app.delete("/file/{file_key}", tags=["Storage"])
async def send_to_trash(
    req: Request, file_key: str, auth=Depends(auth.auth_middleware)
):
    return await deta.send_to_trash(req, file_key)


@app.get("/file/{file_key}", tags=["Storage"])
async def get_file(req: Request, file_key: str, auth=Depends(auth.auth_middleware)):
    return await deta.get_file(req, file_key)


@app.get("/file/{file_key}/download", tags=["Storage"])
async def download_file(
    req: Request, file_key: str, auth=Depends(auth.auth_middleware)
):
    return await deta.download_file(req, file_key)


@app.get("/files", tags=["Storage"])
async def get_files(req: Request, auth=Depends(auth.auth_middleware)):
    return await deta.get_files(req)


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
