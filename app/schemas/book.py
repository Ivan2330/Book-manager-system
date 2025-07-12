from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
import datetime

from app.models.book import Genre

class BookBase(BaseModel):
    title: str = Field(..., min_length=1)
    published_year: int = Field(..., ge=1800, le=datetime.datetime.now().year)
    genre: Genre
    author_id: int

    @validator("title")
    def title_must_not_be_blank(cls, v):
        if not v.strip():
            raise ValueError("Title must not be blank")
        return v


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    published_year: Optional[int] = Field(None, ge=1800, le=datetime.datetime.now().year)
    genre: Optional[Genre] = None
    author_id: Optional[int] = None

class BookOut(BookBase):
    id: int
    author_name: str

    class Config:
        orm_mode = True
