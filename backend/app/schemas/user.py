from pydantic import BaseModel, EmailStr
from typing import Optional

# Schema for creating a new user
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Schema for updating a user
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None

# Schema for reading user data from the database
class UserInDB(BaseModel):
    id: int
    email: str
    password_hash: str

    class Config:
        orm_mode = True

# Schema for API responses (excluding password)
class User(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
