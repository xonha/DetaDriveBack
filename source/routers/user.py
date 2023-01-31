from fastapi import APIRouter

from source import deta, schemas

router = APIRouter()


@router.post("/register", status_code=201)
async def register(user: schemas.UserLogin):
    return await deta.register(user)


@router.post("/login")
async def login(user: schemas.UserLogin):
    return await deta.login(user)


@router.get("")
async def get_users():
    return await deta.get_users()
