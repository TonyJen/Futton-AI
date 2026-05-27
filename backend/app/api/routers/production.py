"""
Production Router (Phase 1/3)

Endpoints matching frontend expectations:
- GET /production/orders
- GET /production/workcenters
- GET /production/orders/{id}
- GET /production/status/summary
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.dependencies import DBSessionDep
from app.db.models import WorkCenter as WorkCenterModel, ProductionOrder as ProductionOrderModel
from app.schemas.production import (
    ProductionOrderDetail,
    ProductionOrderFilter,
    ProductionOrderRead,
)
from app.services.production_service import ProductionService
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/production", tags=["Production"])


@router.get("/orders", response_model=List[dict])
async def list_production_orders(
    db: DBSessionDep,
    status: Optional[str] = Query(None, description="Planned, Released, InProgress, Completed, Cancelled"),
    item_id: Optional[int] = None,
    work_center_id: Optional[int] = None,
    priority_max: Optional[int] = Query(None, le=10),
) -> List[dict]:
    """List production orders shaped for the Production page frontend (with names)."""
    from app.db.models import Item as ItemModel, WorkCenter as WorkCenterModel

    stmt = (
        select(ProductionOrderModel)
        .options(
            selectinload(ProductionOrderModel.item),
            selectinload(ProductionOrderModel.work_center),
        )
        .order_by(ProductionOrderModel.ProductionOrderID.desc())
    )
    if status:
        stmt = stmt.where(ProductionOrderModel.Status == status)

    rows = (await db.execute(stmt)).scalars().all()

    shaped = []
    for o in rows:
        # Apply remaining filters
        if item_id is not None and o.ItemID != item_id:
            continue
        if work_center_id is not None and o.WorkCenterID != work_center_id:
            continue
        if priority_max is not None and (o.Priority or 5) > priority_max:
            continue

        item = o.item
        wc = o.work_center

        shaped.append({
            "productionOrderId": o.ProductionOrderID,
            "orderNumber": o.WorkOrderNumber,
            "itemId": o.ItemID,
            "itemName": item.ItemName if item else "Item",
            "itemCode": item.ItemCode if item else "",
            "quantity": o.OrderQuantity,
            "completedQty": o.QuantityCompleted or 0,
            "status": o.Status,
            "workCenter": wc.WorkCenterName if wc else "",
            "dueDate": o.PlannedCompletionDate,
            "priority": o.Priority or 5,
            "workCenterId": o.WorkCenterID,
        })

    return shaped


@router.get("/orders/{order_id}", response_model=ProductionOrderDetail)
async def get_production_order(
    order_id: int,
    db: DBSessionDep,
) -> ProductionOrderDetail:
    """Detailed view including required vs issued materials."""
    service = ProductionService(db)
    detail = await service.get_order_detail(order_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Production order not found")
    return detail


@router.get("/workcenters", response_model=List[dict])
async def list_workcenters(db: DBSessionDep) -> List[dict]:
    """
    List work centers with computed utilization and active order counts.
    Matches the shape expected by the Production page (WorkCenter TS interface).
    """
    # Get all active work centers
    stmt = select(WorkCenterModel).where(WorkCenterModel.IsActive == True)
    result = await db.execute(stmt)
    work_centers = result.scalars().all()

    # Get active production order counts per work center
    active_statuses = ("Planned", "Released", "InProgress", "On Hold")
    count_stmt = (
        select(
            ProductionOrderModel.WorkCenterID,
            func.count(ProductionOrderModel.ProductionOrderID).label("active_count"),
        )
        .where(ProductionOrderModel.Status.in_(active_statuses))
        .group_by(ProductionOrderModel.WorkCenterID)
    )
    count_result = await db.execute(count_stmt)
    active_counts = {row.WorkCenterID: row.active_count for row in count_result}

    # Get utilization from the existing agent tool logic if possible, otherwise compute simply
    try:
        from app.agents.tools import get_work_center_utilization
        util_map = await get_work_center_utilization(db)
        util_dict = {u["work_center_id"]: u for u in util_map}
    except Exception:
        util_dict = {}

    response = []
    for wc in work_centers:
        util = util_dict.get(wc.WorkCenterID, {})
        active = active_counts.get(wc.WorkCenterID, 0)

        # Simple utilization fallback if the tool didn't return it
        utilization = util.get("utilization_percent", 0) or 0
        if utilization == 0 and active > 0:
            utilization = min(85, 35 + active * 12)  # light heuristic

        status = util.get("status", "Running" if active > 0 else "Idle")

        response.append({
            "workCenterId": wc.WorkCenterID,
            "code": wc.WorkCenterCode,
            "name": wc.WorkCenterName,
            "capacityPerDay": wc.Capacity or 100,
            "currentUtilization": round(utilization),
            "activeOrders": active,
            "status": status,
        })

    return response


@router.get("/status/summary")
async def production_summary(db: DBSessionDep) -> dict:
    """Basic production KPIs (used by dashboards/agents)."""
    service = ProductionService(db)
    orders = await service.list_orders()

    return {
        "total_open": len([o for o in orders if o.Status not in ("Completed", "Cancelled")]),
        "in_progress": len([o for o in orders if o.Status == "InProgress"]),
        "planned": len([o for o in orders if o.Status == "Planned"]),
        "released": len([o for o in orders if o.Status == "Released"]),
    }
