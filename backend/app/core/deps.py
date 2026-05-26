"""
FastAPI dependencies for the Futon Manufacturing ERP backend.
Primary: async database session injection.
"""

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Primary database dependency for all routers and services.
    """
    async for session in get_async_db():
        yield session


def get_current_user_stub():
    """Placeholder for authentication (Phase 1)."""
    return {"user_id": "system", "username": "api_user", "roles": ["admin", "planner"]}


async def get_current_active_user(
    current_user: dict = Depends(get_current_user_stub),
) -> dict:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return current_user
