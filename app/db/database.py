from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import Settings
from fastapi import Depends
from app.core.dependencies import get_settings_dependency

Base = declarative_base()


def get_engine(settings: Settings) -> AsyncEngine:
    return create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        future=True
    )


async def get_db(settings: Settings = Depends(get_settings_dependency)) -> AsyncSession:
    engine = get_engine(settings)
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
