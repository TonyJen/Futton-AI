"""
Tests for the Action Executor.

This is one of the most critical components because it is the only place
that performs real mutations after human approval of agent proposals.
"""

import pytest
from app.db.models import Inventory, Item, PurchaseOrder, PurchaseOrderDetail
from app.services.action_executor import ActionExecutor
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestActionExecutor:
    async def test_create_purchase_order(self, db_session: AsyncSession):
        executor = ActionExecutor(db_session)

        proposal = {
            "action_type": "CREATE_PURCHASE_ORDER",
            "payload": {
                "ItemID": 5,
                "Quantity": 250,
                "WarehouseID": 1,
            },
        }

        result = await executor.execute_proposal(proposal, approved_by="test-user")

        assert result["success"] is True
        assert "purchase_order_id" in result

        # Verify the PO was actually created in the database
        po_id = result["purchase_order_id"]
        po = await db_session.get(PurchaseOrder, po_id)
        assert po is not None
        assert po.Status == "Draft"

        detail = (await db_session.execute(
            select(PurchaseOrderDetail).where(PurchaseOrderDetail.PurchaseOrderID == po_id)
        )).scalar_one()
        assert detail.Quantity == 250
        assert detail.ItemID == 5

    async def test_adjust_inventory_positive(self, db_session: AsyncSession):
        executor = ActionExecutor(db_session)

        # Get initial quantity
        inv = (await db_session.execute(
            select(Inventory).where(Inventory.ItemID == 5, Inventory.WarehouseID == 1)
        )).scalar_one_or_none()
        initial_qty = inv.QuantityOnHand if inv else 0

        proposal = {
            "action_type": "ADJUST_INVENTORY",
            "payload": {
                "ItemID": 5,
                "WarehouseID": 1,
                "Delta": 150,
            },
        }

        result = await executor.execute_proposal(proposal, approved_by="inventory-agent")

        assert result["success"] is True
        assert result["new_quantity"] == initial_qty + 150

    async def test_update_reorder_point(self, db_session: AsyncSession):
        executor = ActionExecutor(db_session)

        # Insert a test item first (in-memory DB has no sample data)
        test_item = Item(
            ItemCode="TEST-001",
            ItemName="Test Component",
            ItemTypeID=1,
            UnitID=1,
            StandardCost=10.0,
            ListPrice=20.0,
            ReorderPoint=100,
        )
        db_session.add(test_item)
        await db_session.flush()

        proposal = {
            "action_type": "UPDATE_REORDER_POINT",
            "payload": {
                "ItemID": test_item.ItemID,
                "NewReorderPoint": 420,
            },
        }

        result = await executor.execute_proposal(proposal, approved_by="inventory-agent")

        assert result["success"] is True
        assert result["new_reorder_point"] == 420

        await db_session.refresh(test_item)
        assert test_item.ReorderPoint == 420

    async def test_unsupported_action_type(self, db_session: AsyncSession):
        executor = ActionExecutor(db_session)

        proposal = {
            "action_type": "DELETE_ALL_DATA",
            "payload": {},
        }

        result = await executor.execute_proposal(proposal, approved_by="bad-agent")

        assert result["success"] is False
        assert "Unsupported action_type" in result["message"]
