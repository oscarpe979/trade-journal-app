import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database.database import Base, engine
from .routers import user, trades


app = FastAPI()

if os.environ.get("ENVIRONMENT") == "production":
    print("Creating production database tables...")
    Base.metadata.create_all(bind=engine)

# Set up CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",  # Default for Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix="/api/v1", tags=["users"])
app.include_router(trades.router, prefix="/api/v1", tags=["trades"])
