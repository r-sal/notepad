import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Use NullPool in test to avoid asyncpg event loop binding issues
pool_class = NullPool if os.environ.get("TESTING") else None
engine = create_async_engine(settings.database_url, echo=False, poolclass=pool_class)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        yield session
