"""
Pydantic schemas for Items (master data).
"""

from typing import Optional

from pydantic import Field

from .common import BaseSchema, TimestampSchema


class ItemBase(BaseSchema):
    ItemCode: str = Field(..., max_length=50)
    ItemName: str = Field(..., max_length=255)
    ItemTypeID: int
    UnitID: int
    Description: Optional[str] = None
    StandardCost: float = 0.0
    ListPrice: float = 0.0
    IsActive: bool = True
    LeadTimeDays: Optional[int] = 0
    ReorderPoint: float = 0.0
    SafetyStock: float = 0.0


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseSchema):
    ItemName: Optional[str] = None
    Description: Optional[str] = None
    StandardCost: Optional[float] = None
    ListPrice: Optional[float] = None
    IsActive: Optional[bool] = None
    LeadTimeDays: Optional[int] = None
    ReorderPoint: Optional[float] = None
    SafetyStock: Optional[float] = None


class ItemRead(ItemBase, TimestampSchema):
    ItemID: int


class ItemWithTypeRead(ItemRead):
    """Includes related lookup names (populated via joins or services)."""
    ItemTypeName: Optional[str] = None
    UnitCode: Optional[str] = None
    UnitName: Optional[str] = None
