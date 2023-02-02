from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from source.auth import AuthHandler
from source.routers import file, trash, user

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


app.include_router(user.router, prefix="/user", tags=["User"])
app.include_router(
    file.router,
    prefix="/file",
    tags=["File"],
    dependencies=[Depends(auth.auth_middleware)],
)
app.include_router(
    trash.router,
    prefix="/trash",
    tags=["Trash"],
    dependencies=[Depends(auth.auth_middleware)],
)

# create a Hello World endpoint
@app.get("/hello")
async def hello():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
