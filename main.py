from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse


from src.auth import AuthHandler
from src import schemas
from src.deta import DetaHelper


app = FastAPI()
auth_handler = AuthHandler()
deta_helper = DetaHelper()


@app.get("/", include_in_schema=False)
async def docs_redirect():
    return RedirectResponse(url="/docs")


@app.get("/auth", tags=["Auth"])
async def auth(auth=Depends(auth_handler.auth_wrapper)):
    return {"auth": auth}


@app.post("/register", status_code=201, tags=["Auth"])
async def register(user: schemas.User):
    if user.username in deta_helper.get_users_list():
        raise HTTPException(status_code=400, detail="Username is taken")

    hashed_password = auth_handler.get_password_hash(user.password)

    deta_helper.insert_user(
        {
            "username": user.username,
            "password": hashed_password,
        }
    )

    return {"message": f"User {user.username} created successfully"}


@app.post("/login", tags=["Auth"])
async def login(user: schemas.User):
    users_list = deta_helper.get_users_list()
    if user.username not in users_list:
        raise HTTPException(status_code=400, detail="Invalid username")

    users_dict = deta_helper.get_users_dict()

    hashed_password = deta_helper.get_hashed_password(users_dict[user.username])
    password_verified = auth_handler.verify_password(user.password, hashed_password)
    if not password_verified:
        raise HTTPException(status_code=400, detail="Invalid password")

    return {"token": auth_handler.encode_token(), "type": "bearer"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
