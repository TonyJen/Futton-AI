"""
Inventory Router (Phase 1)

Key endpoints for inventory visibility and shortage detection.
"""

from typing import List

from fastapi import APIRouter, Query

from app.core.dependencies import DBSessionDep
from app.schemas.inventory import (
    InventoryItemStatus,
    InventoryStatusFilter,
)
from app.services.inventory_service import get_inventory_status

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/status", response_model=List[InventoryItemStatus])
async def get_inventory_status_endpoint(
    db: DBSessionDep,
    below_reorder: bool = Query(False, description="Only show items below reorder point"),
    item_type: str | None = Query(None, description="RAW | COMP | FG"),
    warehouse_id: int | None = Query(None),
    search: str | None = Query(None),
) -> List[InventoryItemStatus]:
    """Inventory status with warehouse breakdown and reorder alerts. Core for MRP and agents."""
    filters = InventoryStatusFilter(
        below_reorder=below_reorder,
        item_type=item_type,
        warehouse_id=warehouse_id,
        search=search,
    )
    return await get_inventory_status(db, filters)


@router.get("/status/summary")
async def inventory_summary(db: DBSessionDep) -> dict:
    """Quick KPI summary (can be expanded)."""
    items = await get_inventory_status(db)
    below = [i for i in items if i.BelowReorderPoint]
    return {
        "total_tracked_items": len(items),
        "items_below_reorder": len(below),
        "critical_shortages": len([i for i in below if i.TotalAvailable < 0]),
    }
