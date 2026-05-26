"""
Pydantic schemas for Bill of Materials.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class BOMExplosionComponent(BaseModel):
    component_item_id: int
    component_name: Optional[str] = None
    quantity: float
    scrap_rate: float = 0.0
    level: int = 0


class BOMExplosionRequest(BaseModel):
    item_id: int
    quantity: float = 1.0


class BOMExplosionResult(BaseModel):
    item_id: int
    quantity: float
    components: List[BOMExplosionComponent] = Field(default_factory=list)
    total_components: int = 0
