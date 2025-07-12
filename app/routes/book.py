from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from typing import List, Optional
import csv, io, json, random
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from app.routes.auth import current_active_user
from app.core.database import get_async_session
from app.models.book import Book, Genre
from app.models.author import Author
from app.models.user import User
from app.schemas.book import BookCreate, BookUpdate, BookOut

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/books", tags=["books"])

# GET /books/recommend
@router.get("/recommend", response_model=List[BookOut])
@limiter.limit("5/minute")
async def recommend_books(
    request: Request,
    genre: Optional[str] = Query(None, description="Must match one of the Genre enum values"),
    author_id: Optional[int] = Query(None),
    exclude_id: Optional[int] = Query(None),
    session: AsyncSession = Depends(get_async_session),
):
    genre_enum = None
    if genre:
        try:
            genre_enum = Genre(genre.capitalize())
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid genre: {genre}")

    query = select(Book).options(joinedload(Book.author))

    if genre_enum:
        query = query.where(Book.genre == genre_enum)
    if author_id:
        query = query.where(Book.author_id == author_id)
    if exclude_id:
        query = query.where(Book.id != exclude_id)

    result = await session.execute(query)
    books = result.scalars().all()

    if not books:
        return []

    sample = random.sample(books, min(5, len(books)))
    return [
        BookOut(
            id=b.id,
            title=b.title,
            genre=b.genre,
            published_year=b.published_year,
            author_id=b.author_id,
            author_name=b.author.name
        ) for b in sample
    ]

# GET /books/export
@router.get("/export")
async def export_books(
    format: str = Query("json", regex="^(json|csv)$"),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(Book).options(joinedload(Book.author))
    )
    books = result.scalars().all()

    data = [
        {
            "id": b.id,
            "title": b.title,
            "genre": b.genre,
            "published_year": b.published_year,
            "author_id": b.author_id,
            "author_name": b.author.name
        }
        for b in books
    ]

    if format == "json":
        return data
    else:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()

# GET /books/all — get all books without filters
@router.get("/all", response_model=List[BookOut])
async def get_all_books(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Book).options(joinedload(Book.author)))
    books = result.scalars().all()
    return [
        BookOut(
            id=b.id,
            title=b.title,
            genre=b.genre,
            published_year=b.published_year,
            author_id=b.author_id,
            author_name=b.author.name
        ) for b in books
    ]


# GET /books/ (with filters, pagination, sorting)
@router.get("/", response_model=List[BookOut])
@limiter.limit("10/minute")
async def get_books(
    request: Request,
    title: Optional[str] = None,
    genre: Optional[Genre] = None,
    author_id: Optional[int] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    sort_by: Optional[str] = Query(None, regex="^(title|published_year|author_id)$"),
    skip: int = 0,
    limit: int = 10,
    session: AsyncSession = Depends(get_async_session),
):
    query = select(Book).options(joinedload(Book.author))

    if title:
        query = query.where(Book.title.ilike(f"%{title}%"))
    if genre:
        query = query.where(Book.genre == genre)
    if author_id:
        query = query.where(Book.author_id == author_id)
    if year_from:
        query = query.where(Book.published_year >= year_from)
    if year_to:
        query = query.where(Book.published_year <= year_to)
    if sort_by:
        query = query.order_by(getattr(Book, sort_by))

    result = await session.execute(query.offset(skip).limit(limit))
    books = result.scalars().all()
    return [
        BookOut(
            id=b.id,
            title=b.title,
            genre=b.genre,
            published_year=b.published_year,
            author_id=b.author_id,
            author_name=b.author.name
        ) for b in books
    ]


# GET /books/{id}
@router.get("/{book_id}", response_model=BookOut)
async def get_book(book_id: int, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        select(Book).options(joinedload(Book.author)).where(Book.id == book_id)
    )
    book = result.scalars().first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return BookOut(
        id=book.id,
        title=book.title,
        genre=book.genre,
        published_year=book.published_year,
        author_id=book.author_id,
        author_name=book.author.name
    )

# POST /books/
@router.post("/", response_model=BookOut)
async def create_book(
    data: BookCreate,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user)
):
    author = await session.get(Author, data.author_id)
    if not author:
        raise HTTPException(status_code=400, detail="Author does not exist")

    book = Book(**data.dict())
    session.add(book)
    await session.commit()
    await session.refresh(book)

    return BookOut(
        id=book.id,
        title=book.title,
        genre=book.genre,
        published_year=book.published_year,
        author_id=book.author_id,
        author_name=author.name
    )

# PUT /books/{book_id}
@router.put("/{book_id}", response_model=BookOut)
async def update_book(
    book_id: int,
    data: BookUpdate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user),
):
    result = await session.execute(
        select(Book).options(joinedload(Book.author)).where(Book.id == book_id)
    )
    book = result.scalars().first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    for field, value in update_data.items():
        setattr(book, field, value)

    await session.commit()
    await session.refresh(book)

    return BookOut(
        id=book.id,
        title=book.title,
        genre=book.genre,
        published_year=book.published_year,
        author_id=book.author_id,
        author_name=book.author.name
    )


# DELETE /books/{id}
@router.delete("/{book_id}")
async def delete_book(
    book_id: int,
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user)
):
    book = await session.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    await session.delete(book)
    await session.commit()
    return {"detail": f"Book {book_id} deleted successfully"}

# POST /books/import
@router.post("/import")
async def import_books(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
    user=Depends(current_active_user)
):
    ext = file.filename.split(".")[-1].lower()
    content = await file.read()

    try:
        if ext == "json":
            books_data = json.loads(content.decode("utf-8"))
        elif ext == "csv":
            reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
            books_data = list(reader)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid file format: {e}")

    imported = 0
    for item in books_data:
        try:
            book = Book(
                title=item["title"].strip(),
                genre=Genre(item["genre"]),
                published_year=int(item["published_year"]),
                author_id=int(item["author_id"])
            )
            session.add(book)
            imported += 1
        except Exception:
            continue

    await session.commit()
    return {"detail": f"Imported {imported} books"}


