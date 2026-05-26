"""Core configuration and dependencies (lazy imports to avoid circular issues)."""

from .config import get_settings, settings

def get_db():
    from .deps import get_db as _get_db
    return _get_db

def get_current_user_stub():
    from .deps import get_current_user_stub as _stub
    return _stub

def get_current_active_user():
    from .deps import get_current_active_user as _active
    return _active

__all__ = ["settings", "get_settings", "get_db", "get_current_user_stub", "get_current_active_user"]
