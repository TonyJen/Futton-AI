"""
Core configuration for Futon Manufacturing ERP Backend.
Uses Pydantic v2 Settings for environment-driven configuration.
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Project
    PROJECT_NAME: str = "Futon Manufacturing ERP"
    PROJECT_VERSION: str = "0.1.0"
    APP_NAME: str = "Futon AI Manufacturing ERP"
    APP_VERSION: str = "0.2.0"
    API_V1_PREFIX: str = "/api/v1"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = Field(default=True, description="Enable debug mode / detailed errors")

    # Database - SQLite with async driver (aiosqlite)
    # Default points to the consolidated data file created by DB agent
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/futon_manufacturing.db",
        description="SQLAlchemy database URL (async SQLite recommended for dev)",
    )
    # For Alembic (often uses sync driver)
    ALEMBIC_DATABASE_URL: str = Field(
        default="sqlite:///./data/futon_manufacturing.db",
        description="Sync SQLite URL used by Alembic migrations",
    )

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
        description="Allowed frontend origins for CORS",
    )
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
        description="Allowed frontend origins for CORS (alias)",
    )

    # Pagination / API defaults
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 200

    # AI / Agents (Phase 2 - placeholders)
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    GROQ_API_KEY: str | None = None
    DEFAULT_LLM_PROVIDER: str = "openai"  # openai | anthropic | groq | ollama

    # Security (future)
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days for dev


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance (singleton pattern)."""
    return Settings()


# Convenience export
settings = get_settings()
