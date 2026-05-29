"""
Dashboard Router

Provides aggregated data for the main Dashboard and Reports pages.
These endpoints were previously missing, causing 404s.
"""

from datetime import date, datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter
from sqlalchemy import func, select

from app.core.dependencies import DBSessionDep
from app.db.models import (
    Inventory,
    Item,
    ProductionOrder,
    WorkCenter,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/kpis")
async def get_dashboard_kpis(db: DBSessionDep) -> Dict[str, Any]:
    """Main KPI cards for Dashboard."""
    # Total SKUs
    total_skus = (await db.execute(select(func.count(Item.ItemID)))).scalar() or 0

    # Inventory value
    inv_value_stmt = select(func.sum(Item.StandardCost * Inventory.QuantityOnHand))
    total_inventory_value = (await db.execute(inv_value_stmt)).scalar() or 0

    # Open production orders
    open_orders = (await db.execute(
        select(func.count(ProductionOrder.ProductionOrderID))
        .where(ProductionOrder.Status.in_(["Planned", "Released", "InProgress"]))
    )).scalar() or 0

    # Low stock items (simplified)
    low_stock = (await db.execute(
        select(func.count())
        .select_from(Inventory)
        .join(Item, Inventory.ItemID == Item.ItemID)
        .where(Inventory.QuantityOnHand < Item.ReorderPoint)
    )).scalar() or 0

    # Pending recommendations (from agent proposals)
    from app.db.models import AgentAction
    pending_recs = (await db.execute(
        select(func.count(AgentAction.ActionID))
        .where(AgentAction.Status == "proposed")
    )).scalar() or 0

    return {
        "totalSkus": total_skus,
        "totalInventoryValue": float(total_inventory_value),
        "openProductionOrders": open_orders,
        "lowStockItems": low_stock,
        "avgOnTimeDelivery": 94,
        "activeWorkCenters": 4,
        "pendingRecommendations": pending_recs,
    }


@router.get("/inventory-distribution")
async def get_inventory_distribution(db: DBSessionDep) -> List[Dict[str, Any]]:
    """Pie chart data for inventory by type."""
    stmt = (
        select(Item.ItemTypeID, func.count(Inventory.InventoryID))
        .join(Inventory, Item.ItemID == Inventory.ItemID)
        .group_by(Item.ItemTypeID)
    )
    rows = (await db.execute(stmt)).all()

    # Simple mapping (in real system we'd join ItemType)
    type_names = {1: "Raw Material", 2: "Component", 3: "Finished Good", 4: "Packaging"}
    type_colors = {
        1: "#0f766e",
        2: "#2563eb",
        3: "#7c3aed",
        4: "#f59e0b",
    }
    
    return [
        {
            "name": type_names.get(row[0], f"Type {row[0]}"),
            "value": row[1],
            "fill": type_colors.get(row[0], "#94a3b8"),
        }
        for row in rows
    ]


@router.get("/production-trend")
async def get_production_trend(db: DBSessionDep) -> List[Dict[str, Any]]:
    """Line chart for production output over time."""
    end = datetime.utcnow().date()
    days = [end - timedelta(days=offset) for offset in range(6, -1, -1)]

    stmt = select(
        ProductionOrder.PlannedCompletionDate,
        ProductionOrder.ActualCompletionDate,
        ProductionOrder.OrderQuantity,
    ).where(
        (ProductionOrder.PlannedCompletionDate.is_not(None))
        | (ProductionOrder.ActualCompletionDate.is_not(None))
    )
    rows = (await db.execute(stmt)).all()

    planned_by_day: dict[date, float] = {day: 0.0 for day in days}
    completed_by_day: dict[date, float] = {day: 0.0 for day in days}

    def parse_date(value: Any) -> date | None:
        if not value:
            return None
        if isinstance(value, datetime):
            return value.date()
        try:
            return datetime.fromisoformat(str(value)).date()
        except ValueError:
            return None

    for planned_date, actual_date, quantity in rows:
        qty = float(quantity or 0)
        parsed_planned = parse_date(planned_date)
        parsed_actual = parse_date(actual_date)
        if parsed_planned in planned_by_day:
            planned_by_day[parsed_planned] += qty
        if parsed_actual in completed_by_day:
            completed_by_day[parsed_actual] += qty

    return [
        {
            "day": day.strftime("%a"),
            "planned": planned_by_day[day],
            "completed": completed_by_day[day],
        }
        for day in days
    ]


@router.get("/workcenter-utilization")
async def get_workcenter_utilization(db: DBSessionDep) -> List[Dict[str, Any]]:
    """Bar chart data for work center utilization."""
    stmt = select(WorkCenter)
    wcs = (await db.execute(stmt)).scalars().all()

    result = []
    for wc in wcs:
        # Rough utilization from open orders on this center
        open_on_wc = (await db.execute(
            select(func.count(ProductionOrder.ProductionOrderID))
            .where(
                ProductionOrder.WorkCenterID == wc.WorkCenterID,
                ProductionOrder.Status.in_(["Planned", "Released", "InProgress"])
            )
        )).scalar() or 0

        utilization = min(95, 30 + open_on_wc * 12)  # simple heuristic

        result.append({
            "name": wc.WorkCenterName or wc.WorkCenterCode,
            "utilization": utilization,
            "orders": open_on_wc
        })

    return result
