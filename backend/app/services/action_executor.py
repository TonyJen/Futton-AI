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

from app.db.models import (
    PurchaseOrder, PurchaseOrderDetail, Inventory, InventoryTransaction, Item,
    SupplierItem,
)


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
        """
        Production-grade PO creation from agent proposals.
        Looks up real supplier pricing via SupplierItem when possible.
        """
        import random
        from datetime import datetime, timedelta

        item_id = payload.get("ItemID")
        qty = float(payload.get("Quantity", 0))
        warehouse_id = payload.get("WarehouseID", 1)
        supplier_id = payload.get("SupplierID", 1)

        # Try to get preferred pricing / lead time
        unit_price = payload.get("UnitPrice", 0.0)
        lead_time = 7

        if item_id:
            stmt = select(SupplierItem).where(
                (SupplierItem.ItemID == item_id) & (SupplierItem.SupplierID == supplier_id)
            ).order_by(SupplierItem.IsPreferred.desc())
            si = (await self.db.execute(stmt)).scalar_one_or_none()
            if si:
                unit_price = si.UnitPrice
                lead_time = si.LeadTimeDays or 7

        # Generate nice PO number
        year = datetime.now().year
        po_number = f"PO-AI-{year}-{random.randint(10000, 99999)}"

        po = PurchaseOrder(
            PONumber=po_number,
            SupplierID=supplier_id,
            WarehouseID=warehouse_id,
            OrderDate=datetime.now().strftime("%Y-%m-%d"),
            ExpectedDeliveryDate=(datetime.now() + timedelta(days=lead_time)).strftime("%Y-%m-%d"),
            Status="Draft",
            CreatedBy=f"AI Agent (approved by {approved_by})",
            Notes="Created from approved agent recommendation",
        )
        self.db.add(po)
        await self.db.flush()

        # Single line for now (MRP proposals are per-item)
        detail = PurchaseOrderDetail(
            PurchaseOrderID=po.PurchaseOrderID,
            LineNumber=1,
            ItemID=item_id,
            Quantity=qty,
            UnitPrice=unit_price or 0.0,
            QuantityReceived=0.0,
        )
        self.db.add(detail)

        subtotal = qty * (unit_price or 0.0)
        po.Subtotal = subtotal
        po.TotalAmount = subtotal  # taxes/shipping added later in UI

        await self.db.commit()
        await self.db.refresh(po)

        return {
            "success": True,
            "purchase_order_id": po.PurchaseOrderID,
            "po_number": po.PONumber,
            "message": f"Purchase Order {po.PONumber} created from agent proposal",
            "item_id": item_id,
            "quantity": qty,
            "unit_price": unit_price,
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
