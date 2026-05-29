"""
Core configuration for Futon Manufacturing ERP Backend.
Uses Pydantic v2 Settings for environment-driven configuration.
"""

from functools import lru_cache
from typing import List, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        # Look for .env in both the backend folder and the project root
        # (important because start.ps1 runs uvicorn from the backend/ directory)
        env_file=(".env", "../.env"),
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
    APP_ENV: Literal["development", "test", "production"] = Field(
        default="development",
        description="Runtime environment name used for operational defaults",
    )
    DEBUG: bool = Field(default=False, description="Enable debug mode / detailed errors")
    SQL_ECHO: bool = Field(default=False, description="Enable SQLAlchemy SQL echo logging")
    QUERY_TIMING_ENABLED: bool = Field(
        default=False,
        description="Log queries that exceed the slow query threshold",
    )
    SLOW_QUERY_THRESHOLD_MS: int = Field(
        default=250,
        description="Warn when a DB query exceeds this threshold in milliseconds",
    )

    # Database - SQLite with async driver (aiosqlite)
    # Default points to the consolidated data file created by DB agent
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/futon_manufacturing.db",
        description="SQLAlchemy database URL (SQLite is suitable for dev/demo only)",
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
    XAI_API_KEY: str | None = None
    DEFAULT_LLM_PROVIDER: str = "xai"  # xai | openai | anthropic | groq | ollama

    # LLM Model names (you can override these)
    OPENAI_MODEL: str = "gpt-4o-mini"
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    XAI_MODEL: str = "grok-3"   # xAI Grok models (check console.x.ai for current names)

    # Security (future)
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days for dev


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance (singleton pattern)."""
    return Settings()


# Convenience export
settings = get_settings()
