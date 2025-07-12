from pydantic import BaseModel, Field
from typing import Optional


class AuthorBase(BaseModel):
    name: str = Field(..., min_length=1)

    @staticmethod
    def validate_name(name: str) -> str:
        if not name.strip():
            raise ValueError("Author name cannot be empty")
        return name


class AuthorCreate(AuthorBase):
    pass


class AuthorOut(AuthorBase):
    id: int

    class Config:
        orm_mode = True
