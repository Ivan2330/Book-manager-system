from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from app.core.config import settings

Base = declarative_base()


engine = create_async_engine(
    settings.database_url,
    echo=True
)

async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

async def get_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    from app.models.user import User
    yield SQLAlchemyUserDatabase(session, User)
