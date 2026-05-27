"""
Inventory Router (Phase 1)

Key endpoints for inventory visibility and shortage detection.
"""

from typing import List, Optional

from fastapi import APIRouter, Query

from app.core.dependencies import DBSessionDep

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("", response_model=List[dict])
async def list_inventory(db: DBSessionDep, warehouse: Optional[str] = None):
    """Basic inventory list (placeholder until full schema is aligned)."""
    from app.db.models import Inventory as InventoryModel, Item as ItemModel
    from sqlalchemy import select

    stmt = (
        select(InventoryModel, ItemModel)
        .join(ItemModel, InventoryModel.ItemID == ItemModel.ItemID)
        .limit(200)
    )
    rows = (await db.execute(stmt)).all()

    result = []
    for inv, item in rows:
        result.append({
            "inventoryId": inv.InventoryID,
            "itemId": item.ItemID,
            "itemCode": item.ItemCode,
            "itemName": item.ItemName,
            "warehouseId": inv.WarehouseID,
            "quantityOnHand": inv.QuantityOnHand or 0,
            "quantityAllocated": inv.QuantityAllocated or 0,
            "available": (inv.QuantityOnHand or 0) - (inv.QuantityAllocated or 0),
        })
    return result


# Note: Full inventory status endpoints are temporarily simplified.
# The basic /inventory list endpoint above is active for the frontend.


@router.get("/transactions", response_model=List[dict])
async def list_inventory_transactions(
    db: DBSessionDep,
    itemId: Optional[int] = Query(None, alias="itemId"),
    limit: int = Query(50, le=200),
):
    """Return recent inventory transactions (stub until full InventoryTransaction model + service is wired)."""
    from app.db.models import InventoryTransaction as TxModel, Item as ItemModel
    from sqlalchemy import select, desc

    stmt = (
        select(TxModel, ItemModel)
        .join(ItemModel, TxModel.ItemID == ItemModel.ItemID, isouter=True)
        .order_by(desc(TxModel.TransactionDate))
        .limit(limit)
    )
    if itemId:
        stmt = stmt.where(TxModel.ItemID == itemId)

    rows = (await db.execute(stmt)).all()

    result = []
    for tx, item in rows:
        result.append({
            "transactionId": tx.TransactionID,
            "itemId": tx.ItemID,
            "itemCode": getattr(item, "ItemCode", None),
            "itemName": getattr(item, "ItemName", None),
            "transactionType": tx.TransactionType,
            "quantity": tx.Quantity,
            "quantityBefore": tx.QuantityBefore,
            "quantityAfter": tx.QuantityAfter,
            "referenceType": tx.ReferenceType,
            "referenceId": tx.ReferenceID,
            "transactionDate": tx.TransactionDate.isoformat() if tx.TransactionDate else None,
            "notes": tx.Notes,
        })
    return result
