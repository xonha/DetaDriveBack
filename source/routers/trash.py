from fastapi import APIRouter, Request

from source import deta

router = APIRouter()


@router.get("", tags=["Trash"])
async def get_trash(req: Request):
    return await deta.get_trash(req)


@router.patch("/{file_key}", tags=["Trash"])
async def restore_file(req: Request, file_key: str):
    return await deta.restore_file(req, file_key)


@router.delete("/{file_key}", tags=["Trash"])
async def delete_file(req: Request, file_key: str):
    return await deta.delete_file(req, file_key)
