"""
Business logic for Bill of Materials (BOM).

Core capability for Phase 1: Recursive multi-level BOM explosion.
This is the foundation for MRP, production planning, and costing.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import BillOfMaterial, Item, UnitOfMeasure
from app.schemas.bom import (
    BOMExplosionComponent,
    BOMExplosionResult,
)


class BOMService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_item(self, item_id: int) -> Optional[Item]:
        result = await self.db.execute(
            select(Item).where(Item.ItemID == item_id)
        )
        return result.scalar_one_or_none()

    async def get_bom_children(self, parent_item_id: int) -> List[BillOfMaterial]:
        """Fetch direct children for a parent, eagerly loading component details."""
        stmt = (
            select(BillOfMaterial)
            .where(
                BillOfMaterial.ParentItemID == parent_item_id,
                BillOfMaterial.IsActive.is_(True),
            )
            .options(
                selectinload(BillOfMaterial.component_item),
                selectinload(BillOfMaterial.unit),
            )
            .order_by(BillOfMaterial.BOMLevel, BillOfMaterial.BOMID)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def explode_bom(
        self,
        parent_item_id: int,
        parent_quantity: float = 1.0,
        max_depth: int = 20,
    ) -> BOMExplosionResult:
        """
        Recursively explode a multi-level BOM.

        Returns a flat list of all required components with:
        - Total quantity required (accounting for scrap at every level)
        - Level depth
        - Full traceability back to parent

        This is the canonical implementation that agents and production
        planning will rely on.
        """
        parent_item = await self.get_item(parent_item_id)
        if not parent_item:
            raise ValueError(f"Item with ID {parent_item_id} not found")

        components: List[BOMExplosionComponent] = []
        max_level_reached = 0

        async def _recurse(
            current_parent_id: int,
            current_parent_code: str,
            qty_multiplier: float,
            current_level: int,
        ) -> None:
            nonlocal max_level_reached

            if current_level > max_depth:
                return  # safety guard against infinite recursion in bad data

            children = await self.get_bom_children(current_parent_id)

            for bom in children:
                comp_item = bom.component_item
                if not comp_item or not comp_item.IsActive:
                    continue

                # Effective quantity including scrap
                scrap_factor = 1.0 + (bom.ScrapRate or 0.0) / 100.0
                this_level_qty = bom.Quantity * scrap_factor * qty_multiplier

                unit_code = bom.unit.UnitCode if bom.unit else None

                component = BOMExplosionComponent(
                    ComponentItemID=comp_item.ItemID,
                    ComponentItemCode=comp_item.ItemCode,
                    ComponentItemName=comp_item.ItemName,
                    QuantityPerParent=bom.Quantity,
                    TotalQuantityRequired=round(this_level_qty, 4),
                    UnitCode=unit_code,
                    ScrapRate=bom.ScrapRate or 0.0,
                    Level=current_level,
                    ParentItemID=current_parent_id,
                    ParentItemCode=current_parent_code,
                )
                components.append(component)
                max_level_reached = max(max_level_reached, current_level)

                # Recurse deeper
                await _recurse(
                    current_parent_id=comp_item.ItemID,
                    current_parent_code=comp_item.ItemCode,
                    qty_multiplier=this_level_qty,
                    current_level=current_level + 1,
                )

        # Kick off recursion at level 1 (direct components)
        await _recurse(
            current_parent_id=parent_item.ItemID,
            current_parent_code=parent_item.ItemCode,
            qty_multiplier=parent_quantity,
            current_level=1,
        )

        return BOMExplosionResult(
            ParentItemID=parent_item.ItemID,
            ParentItemCode=parent_item.ItemCode,
            ParentItemName=parent_item.ItemName,
            TotalComponents=len(components),
            MaxLevel=max_level_reached,
            Components=components,
        )

    async def get_bom_tree(self, parent_item_id: int) -> dict:
        """
        Alternative tree-shaped response (optional, useful for React Flow visualization).
        Can be implemented later using the same recursive engine.
        """
        # Placeholder for future tree format
        explosion = await self.explode_bom(parent_item_id)
        return {
            "root": parent_item_id,
            "flat_components": [c.model_dump() for c in explosion.Components],
            "note": "Use explode_bom for the primary flat structure. Tree view coming in Phase 2.",
        }
