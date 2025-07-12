from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.models.author import Author
from app.schemas.author import AuthorCreate, AuthorOut
from app.core.database import get_async_session
from app.routes.auth import current_active_user

router = APIRouter(prefix="/authors", tags=["authors"])

# GET /authors/
@router.get("/", response_model=List[AuthorOut])
async def get_authors(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Author))
    return result.scalars().all()

# GET /authors/{author_id}
@router.get("/{author_id}", response_model=AuthorOut)
async def get_author(author_id: int, session: AsyncSession = Depends(get_async_session)):
    author = await session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author

# POST /authors/
@router.post("/", response_model=AuthorOut)
async def create_author(
    data: AuthorCreate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user)
):
    existing = await session.execute(select(Author).where(Author.name == data.name))
    if existing.scalar():
        raise HTTPException(status_code=400, detail="Author already exists")

    author = Author(name=data.name)
    session.add(author)
    await session.commit()
    await session.refresh(author)
    return author

# PUT /authors/{author_id}
@router.put("/{author_id}", response_model=AuthorOut)
async def update_author(
    author_id: int,
    data: AuthorCreate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user)
):
    author = await session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    author.name = data.name
    await session.commit()
    await session.refresh(author)
    return author

# DELETE /authors/{author_id}
@router.delete("/{author_id}")
async def delete_author(
    author_id: int,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user)
):
    author = await session.get(Author, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    await session.delete(author)
    await session.commit()
    return {"detail": f"Author {author_id} deleted successfully"}
