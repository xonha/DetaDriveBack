from typing import List

from fastapi import APIRouter, Request, UploadFile

from source import deta, schemas

router = APIRouter()


@router.post("")
async def upload_files(req: Request, files: List[UploadFile]):
    return await deta.upload_files(req, files)


@router.post("/{file_key}/share")
async def share_file(req: Request, file_key: str, share_with: str):
    return await deta.share_file(req, file_key, share_with)


@router.patch("/{file_key}/rename")
async def rename_file(req: Request, file_key: str, body: schemas.BodyRename):
    return await deta.rename_file(req, file_key, body.name)


@router.patch("/{file_key}/change_owner")
async def change_owner(req: Request, file_key: str, body: schemas.BodyChangeOwner):
    return await deta.change_owner(req, file_key, body.owner_key)


@router.patch("/{file_key}/send_to_trash")
async def send_to_trash(req: Request, file_key: str):
    return await deta.send_to_trash(req, file_key)


@router.delete("/{file_key}/stop_seeing")
async def stop_seeing(req: Request, file_key: str):
    return await deta.stop_seeing(req, file_key)


@router.get("/owned")
async def get_owned_files(req: Request):
    return await deta.get_owned_files(req)


@router.get("/shared")
async def get_shared_files(req: Request):
    return await deta.get_shared_files(req)


@router.get("/{file_key}")
async def get_file(req: Request, file_key: str):
    return await deta.get_file(req, file_key)


@router.get("/{file_key}/download")
async def download_file(req: Request, file_key: str):
    return await deta.download_file(req, file_key)
