"""
Database session management for Futon Manufacturing ERP.
Async-first with SQLAlchemy 2.0 + aiosqlite for SQLite.
Includes both async runtime sessions and a sync engine for Alembic migrations.
"""

from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# =============================================================================
# ASYNC ENGINE & SESSION (primary for FastAPI runtime)
# =============================================================================

ASYNC_SQLITE_CONNECT_ARGS = {"check_same_thread": False}

async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    connect_args=ASYNC_SQLITE_CONNECT_ARGS if "sqlite" in settings.DATABASE_URL else {},
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# =============================================================================
# SYNC ENGINE & SESSION (used by Alembic)
# =============================================================================

SYNC_DATABASE_URL = settings.ALEMBIC_DATABASE_URL or settings.DATABASE_URL.replace(
    "+aiosqlite", ""
)

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in SYNC_DATABASE_URL else {},
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
    future=True,
)


def get_sync_db() -> Session:
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()


# =============================================================================
# Utility helpers
# =============================================================================

async def init_db() -> None:
    from app.db.models import Base
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    await async_engine.dispose()
    sync_engine.dispose()
