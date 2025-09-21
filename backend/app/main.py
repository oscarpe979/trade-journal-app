from fastapi import FastAPI

from .routers import user

from .database.database import engine
from .database.database import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router, prefix="/api/v1", tags=["users"])


@app.get("/")
def read_root():
    return {"Hello": "World"}
