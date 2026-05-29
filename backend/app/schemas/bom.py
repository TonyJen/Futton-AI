"""
Pydantic schemas for Bill of Materials.
Rich models matching the actual implementation in bom_service.explode_bom.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BOMExplosionComponent(BaseModel):
    """One component in a multi-level BOM explosion."""
    model_config = ConfigDict(populate_by_name=True)

    ComponentItemID: int
    ComponentItemCode: Optional[str] = None
    ComponentItemName: Optional[str] = None
    QuantityPerParent: float
    TotalQuantityRequired: float
    UnitCode: Optional[str] = None
    ScrapRate: float = 0.0
    Level: int = 0
    ParentItemID: int
    ParentItemCode: Optional[str] = None


class BOMExplosionRequest(BaseModel):
    item_id: int
    quantity: float = 1.0


class BOMExplosionResult(BaseModel):
    """Full recursive BOM explosion result."""
    model_config = ConfigDict(populate_by_name=True)

    ParentItemID: int
    ParentItemCode: Optional[str] = None
    ParentItemName: Optional[str] = None
    TotalComponents: int = 0
    MaxLevel: int = 0
    Components: List[BOMExplosionComponent] = Field(default_factory=list)
