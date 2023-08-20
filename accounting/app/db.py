from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.settings import settings

engine = create_async_engine(
    settings.DB_URI,
    pool_pre_ping=True,
    echo=settings.ECHO_SQL,
)

async_session = async_sessionmaker(
    engine,
    autoflush=False,
    future=True,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session.begin() as session:
        yield session
