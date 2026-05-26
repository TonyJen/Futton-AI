"""
Action Executor

THIS IS THE ONLY MODULE ALLOWED TO PERFORM REAL BUSINESS MUTATIONS
as a result of agent proposals being approved by humans.

Supported action_types (extend as needed):
- CREATE_PURCHASE_ORDER
- ADJUST_INVENTORY
- UPDATE_REORDER_POINT
- RELEASE_PRODUCTION_ORDER
"""

from __future__ import annotations

import json
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import PurchaseOrder, PurchaseOrderDetail, Inventory, InventoryTransaction, Item


class ActionExecutor:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_proposal(self, proposal: Dict[str, Any], approved_by: str) -> Dict[str, Any]:
        action_type = proposal.get("action_type")
        payload = proposal.get("payload", {})

        if action_type == "CREATE_PURCHASE_ORDER":
            return await self._create_purchase_order(payload, approved_by)
        elif action_type == "ADJUST_INVENTORY":
            return await self._adjust_inventory(payload, approved_by)
        elif action_type == "UPDATE_REORDER_POINT":
            return await self._update_reorder_point(payload)
        else:
            return {"success": False, "message": f"Unsupported action_type: {action_type}"}

    async def _create_purchase_order(self, payload: Dict[str, Any], approved_by: str) -> Dict[str, Any]:
        # Very simplified PO creation for Phase 1
        po = PurchaseOrder(
            PONumber=f"PO-AI-{approved_by[:3].upper()}{__import__('random').randint(1000,9999)}",
            SupplierID=payload.get("SupplierID", 1),
            WarehouseID=payload.get("WarehouseID", 1),
            Status="Draft",
            CreatedBy=f"AI-Agent (approved by {approved_by})",
        )
        self.db.add(po)
        await self.db.flush()

        detail = PurchaseOrderDetail(
            PurchaseOrderID=po.PurchaseOrderID,
            LineNumber=1,
            ItemID=payload.get("ItemID"),
            Quantity=payload.get("Quantity", 0),
            UnitPrice=payload.get("UnitPrice", 0.0),
        )
        self.db.add(detail)
        await self.db.commit()

        return {
            "success": True,
            "purchase_order_id": po.PurchaseOrderID,
            "message": f"Purchase Order {po.PONumber} created",
        }

    async def _adjust_inventory(self, payload: Dict[str, Any], approved_by: str) -> Dict[str, Any]:
        item_id = payload["ItemID"]
        warehouse_id = payload.get("WarehouseID", 1)
        delta = float(payload.get("Delta", 0))

        stmt = select(Inventory).where(
            (Inventory.ItemID == item_id) & (Inventory.WarehouseID == warehouse_id)
        )
        inv = (await self.db.execute(stmt)).scalar_one_or_none()

        if not inv:
            inv = Inventory(ItemID=item_id, WarehouseID=warehouse_id, QuantityOnHand=0)
            self.db.add(inv)

        inv.QuantityOnHand = (inv.QuantityOnHand or 0) + delta

        tx = InventoryTransaction(
            ItemID=item_id,
            WarehouseID=warehouse_id,
            TransactionTypeID=7,  # ADJ-POS or similar - adjust as needed
            Quantity=delta,
            Notes=f"Approved by AI agent - {approved_by}",
            CreatedBy=approved_by,
        )
        self.db.add(tx)
        await self.db.commit()

        return {"success": True, "new_quantity": float(inv.QuantityOnHand)}

    async def _update_reorder_point(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        item_id = payload["ItemID"]
        new_reorder = float(payload.get("NewReorderPoint", 0))

        item = await self.db.get(Item, item_id)
        if item:
            item.ReorderPoint = new_reorder
            await self.db.commit()
            return {"success": True, "item_id": item_id, "new_reorder_point": new_reorder}
        return {"success": False, "message": "Item not found"}


async def get_executor(db: AsyncSession) -> ActionExecutor:
    return ActionExecutor(db)
