from fastapi import FastAPI

from .routers import user

app = FastAPI()

app.include_router(user.router, prefix="/api/v1", tags=["users"])


@app.get("/")
def read_root():
    return {"Hello": "World"}
