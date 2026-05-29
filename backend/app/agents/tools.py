"""
Manufacturing tools for LangGraph agents.

These are safe (mostly read-only + calculations). Agents use them to gather
information before proposing actions.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    BillOfMaterials,
    Inventory,
    InventoryTransaction,
    Item,
    ProductionOrder,
    TransactionType,
)


def get_manufacturing_tools(db: AsyncSession) -> List:
    """
    Returns a list of tool functions the agents can call.
    In a full implementation these would be decorated with @tool from langchain.
    For now we return plain async callables.
    """
    return [
        explode_bill_of_materials,
        find_low_stock_and_shortages,
        get_item_inventory_status,
        calculate_mrp_requirements,
        run_abc_analysis,
        get_work_center_utilization,
        get_open_production_orders,
    ]


async def explode_bill_of_materials(db: AsyncSession, item_id: int, quantity: float = 1.0) -> Dict[str, Any]:
    """Recursively explodes the BOM for an item."""
    # Simplified version - in reality this would call the bom_service
    result = {
        "item_id": item_id,
        "quantity": quantity,
        "components": [],
        "total_raw_materials": {},
    }

    # Basic recursive lookup (placeholder - real version should be deeper)
    stmt = select(BillOfMaterials).where(BillOfMaterials.ParentItemID == item_id)
    bom_rows = (await db.execute(stmt)).scalars().all()

    for row in bom_rows:
        result["components"].append({
            "component_item_id": row.ComponentItemID,
            "quantity": float(row.Quantity) * quantity,
            "scrap_rate": float(row.ScrapRate or 0),
        })

    return result


async def find_low_stock_and_shortages(db: AsyncSession, threshold_multiplier: float = 1.0) -> List[Dict[str, Any]]:
    """Finds items below reorder point or with shortages."""
    stmt = (
        select(Inventory, Item)
        .join(Item, Inventory.ItemID == Item.ItemID)
        .where(Inventory.QuantityOnHand < Item.ReorderPoint * threshold_multiplier)
    )
    rows = (await db.execute(stmt)).all()

    results = []
    for inv, item in rows:
        results.append({
            "item_id": item.ItemID,
            "item_name": item.ItemName,
            "quantity_available": float(inv.QuantityOnHand or 0),
            "reorder_point": float(item.ReorderPoint or 0),
            "shortage": float(item.ReorderPoint or 0) - float(inv.QuantityOnHand or 0),
        })
    return results


async def run_abc_analysis(db: AsyncSession) -> List[Dict[str, Any]]:
    """
    Real ABC analysis based on recent transaction volume + inventory value.
    A = High turnover or high value items (should be tightly controlled)
    B = Medium importance
    C = Low turnover / low value
    """
    from app.db.models import Item

    # Get all items with their current inventory value
    stmt = select(Item, Inventory).join(Inventory, Item.ItemID == Inventory.ItemID, isouter=True)
    rows = (await db.execute(stmt)).all()

    items_with_metrics = []
    for item, inv in rows:
        # Calculate approximate annual usage from transactions (last 90 days as proxy)
        tx_stmt = (
            select(func.sum(func.abs(InventoryTransaction.Quantity)))
            .join(
                TransactionType,
                InventoryTransaction.TransactionTypeID == TransactionType.TransactionTypeID,
            )
            .where(
                InventoryTransaction.ItemID == item.ItemID,
                InventoryTransaction.TransactionDate >= datetime.now() - timedelta(days=90),
                TransactionType.TypeName.in_(["Issue", "Receipt"]),
            )
        )
        tx_result = await db.execute(tx_stmt)
        usage = abs(float(tx_result.scalar() or 0))

        value = float(item.StandardCost or 0) * (inv.QuantityOnHand or 0) if inv else 0

        # Simple ABC scoring: combine usage volume + inventory value
        score = (usage * 0.6) + (value / 100 * 0.4)

        items_with_metrics.append({
            "item_id": item.ItemID,
            "item_name": item.ItemName,
            "score": score,
            "usage_90d": usage,
            "inventory_value": round(value, 2),
        })

    # Sort by score descending and assign ABC classes
    items_with_metrics.sort(key=lambda x: x["score"], reverse=True)
    total = len(items_with_metrics)

    result = []
    for i, item in enumerate(items_with_metrics):
        if i < total * 0.2:
            abc_class = "A"
        elif i < total * 0.5:
            abc_class = "B"
        else:
            abc_class = "C"

        result.append({
            "item_id": item["item_id"],
            "item_name": item["item_name"],
            "class": abc_class,
            "score": round(item["score"], 1),
            "usage_90d": item["usage_90d"],
            "inventory_value": item["inventory_value"],
        })

    return result


async def get_item_inventory_status(db: AsyncSession, item_id: int) -> Dict[str, Any]:
    """Returns current inventory position for an item across warehouses."""
    stmt = select(Inventory).where(Inventory.ItemID == item_id)
    rows = (await db.execute(stmt)).scalars().all()

    total = sum(float(r.quantity_available or 0) for r in rows)
    return {
        "item_id": item_id,
        "total_available": total,
        "warehouses": [
            {
                "warehouse_id": r.WarehouseID,
                "available": float(r.quantity_available or 0),
            }
            for r in rows
        ],
    }


async def calculate_mrp_requirements(db: AsyncSession, item_id: int, quantity: float) -> Dict[str, Any]:
    """Very simplified MRP calculation."""
    explosion = await explode_bill_of_materials(db, item_id, quantity)
    return {
        "item_id": item_id,
        "gross_requirement": quantity,
        "components_required": explosion.get("components", []),
    }


async def get_work_center_utilization(db: AsyncSession) -> List[Dict[str, Any]]:
    """Returns current work center capacity and active orders (for scheduler)."""
    from app.db.models import WorkCenter
    stmt = select(WorkCenter)
    wcs = (await db.execute(stmt)).scalars().all()
    return [
        {
            "work_center_id": wc.WorkCenterID,
            "name": wc.Name or wc.Code,
            "capacity_per_day": wc.CapacityPerDay or 100,
            "current_utilization": wc.CurrentUtilization or 70,
            "active_orders": wc.ActiveOrders or 1,
            "status": wc.Status or "Running",
        }
        for wc in wcs
    ]


async def get_open_production_orders(db: AsyncSession) -> List[Dict[str, Any]]:
    """Returns open/released production orders for scheduling decisions."""
    stmt = select(ProductionOrder).where(ProductionOrder.Status.in_(["Released", "Planned", "In Progress"]))
    orders = (await db.execute(stmt)).scalars().all()
    return [
        {
            "production_order_id": po.ProductionOrderID,
            "order_number": po.OrderNumber,
            "item_id": po.ItemID,
            "quantity": float(po.Quantity or 0),
            "status": po.Status,
            "work_center": po.WorkCenter,
            "due_date": po.DueDate,
            "priority": po.Priority or "Normal",
        }
        for po in orders
    ]
