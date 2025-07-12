from pydantic import BaseModel, EmailStr
from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    id: int
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str


class UserUpdate(schemas.BaseUserUpdate):
    password: str | None = None
