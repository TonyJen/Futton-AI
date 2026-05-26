"""
Production Orders Router (Phase 1)

Provides list + detail for the Production Command Center.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.dependencies import DBSessionDep
from app.schemas.production import (
    ProductionOrderDetail,
    ProductionOrderFilter,
    ProductionOrderRead,
)
from app.services.production_service import (
    get_production_order_detail,
    list_production_orders,
)

router = APIRouter(prefix="/production-orders", tags=["Production"])


@router.get("", response_model=List[ProductionOrderRead])
async def list_production_orders_endpoint(
    db: DBSessionDep,
    status: Optional[str] = Query(None, description="Planned, Released, InProgress, Completed, Cancelled"),
    item_id: Optional[int] = None,
    work_center_id: Optional[int] = None,
    priority_max: Optional[int] = Query(None, le=10),
) -> List[ProductionOrderRead]:
    """List production orders. Supports basic filters used by dashboard and agents."""
    filters = ProductionOrderFilter(
        status=status,
        item_id=item_id,
        work_center_id=work_center_id,
        priority_max=priority_max,
    )
    return await list_production_orders(db, filters)


@router.get("/{order_id}", response_model=ProductionOrderDetail)
async def get_production_order(
    order_id: int,
    db: DBSessionDep,
) -> ProductionOrderDetail:
    """Detailed view including required vs issued materials (for material availability checks)."""
    detail = await get_production_order_detail(db, order_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Production order not found")
    return detail


@router.get("/status/summary")
async def production_summary(db: DBSessionDep) -> dict:
    """Basic production KPIs."""
    orders = await list_production_orders(db)
    return {
        "total_open": len([o for o in orders if o.Status not in ("Completed", "Cancelled")]),
        "in_progress": len([o for o in orders if o.Status == "InProgress"]),
        "planned": len([o for o in orders if o.Status == "Planned"]),
    }
