"""
Compatibility shim for dependencies.

Some code expects app.core.dependencies.DBSessionDep.
We re-export from deps.py.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .deps import get_db as _get_db

# Common dependency used across the app
DBSessionDep = Annotated[AsyncSession, Depends(_get_db)]

# Also expose get_db for direct use
get_db = _get_db
