"""
Manufacturing tools for LangGraph agents.

These are safe (mostly read-only + calculations). Agents use them to gather
information before proposing actions.
"""

from __future__ import annotations

from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.models import (
    Item, Inventory, BillOfMaterials, ProductionOrder, ProductionOrderMaterial,
    PurchaseOrder, SupplierItem
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
        .where(Inventory.QuantityAvailable < Item.ReorderPoint * threshold_multiplier)
    )
    rows = (await db.execute(stmt)).all()

    results = []
    for inv, item in rows:
        results.append({
            "item_id": item.ItemID,
            "item_name": item.ItemName,
            "quantity_available": float(inv.QuantityAvailable or 0),
            "reorder_point": float(item.ReorderPoint or 0),
            "shortage": float(item.ReorderPoint or 0) - float(inv.QuantityAvailable or 0),
        })
    return results


async def run_abc_analysis(db: AsyncSession) -> List[Dict[str, Any]]:
    """Placeholder ABC analysis (returns some items as A/B/C)."""
    # In a real system this would be a proper query
    return [
        {"item_id": 5, "class": "A", "turnover": 4.2},
        {"item_id": 12, "class": "B", "turnover": 1.8},
    ]


async def get_item_inventory_status(db: AsyncSession, item_id: int) -> Dict[str, Any]:
    """Returns current inventory position for an item across warehouses."""
    stmt = select(Inventory).where(Inventory.ItemID == item_id)
    rows = (await db.execute(stmt)).scalars().all()

    total = sum(float(r.QuantityAvailable or 0) for r in rows)
    return {
        "item_id": item_id,
        "total_available": total,
        "warehouses": [
            {
                "warehouse_id": r.WarehouseID,
                "available": float(r.QuantityAvailable or 0),
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
