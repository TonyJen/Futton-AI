"""
Common Pydantic schemas, base models, and pagination helpers.
"""

from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Base Configuration
# =============================================================================

class BaseSchema(BaseModel):
    """Base schema with common ORM configuration."""

    model_config = ConfigDict(
        from_attributes=True,  # Enable .model_validate(orm_obj)
        populate_by_name=True,
        use_enum_values=True,
    )


class TimestampSchema(BaseSchema):
    CreatedDate: Optional[datetime] = None
    ModifiedDate: Optional[datetime] = None


# =============================================================================
# Pagination
# =============================================================================

T = TypeVar("T")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response wrapper."""

    items: List[T]
    total: int
    page: int = 1
    page_size: int = 50
    has_next: bool = False


class ListQueryParams(BaseSchema):
    """Common query parameters for list endpoints."""

    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=200)
    search: Optional[str] = None
    is_active: Optional[bool] = None


# =============================================================================
# Standard Response
# =============================================================================

class MessageResponse(BaseSchema):
    message: str
    success: bool = True


class ErrorResponse(BaseSchema):
    detail: str
    code: Optional[str] = None
