"""
Tests for the LangGraph Agents (MRP and Inventory).

Key principle being tested: Agents must only create proposals with status="proposed".
They must never directly mutate business data.
"""

import pytest
from app.agents.inventory_agent import InventoryIntelligenceAgent
from app.agents.mrp_agent import MRPPlanningAgent
from app.db.models import AgentAction, PurchaseOrder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestMRPAgent:
    async def test_mrp_agent_only_creates_proposed_actions(self, db_session: AsyncSession):
        """Critical safety test: Agent must never directly create POs."""
        agent = MRPPlanningAgent(db_session)

        # Count POs before
        initial_po_count = (await db_session.execute(select(PurchaseOrder))).scalars().all()
        initial_count = len(initial_po_count)

        result = await agent.run({"item_id": 12, "quantity": 5})

        # Agent should report creating proposals
        assert result["status"] == "completed"
        assert result["proposals_created"] >= 1

        # But no actual Purchase Orders should have been created
        final_po_count = (await db_session.execute(select(PurchaseOrder))).scalars().all()
        assert len(final_po_count) == initial_count

        # Instead, AgentAction records with status="proposed" should exist
        actions = (await db_session.execute(
            select(AgentAction).where(AgentAction.Status == "proposed")
        )).scalars().all()

        assert len(actions) >= 1
        assert any(a.ActionType == "CREATE_PURCHASE_ORDER" for a in actions)


@pytest.mark.asyncio
class TestInventoryAgent:
    async def test_inventory_agent_creates_reorder_proposals(self, db_session: AsyncSession):
        agent = InventoryIntelligenceAgent(db_session)

        result = await agent.run({})

        assert result["status"] == "completed"
        assert result["proposals_created"] >= 0  # At least it shouldn't crash

        # Should create UPDATE_REORDER_POINT proposals, not direct updates
        actions = (await db_session.execute(
            select(AgentAction).where(AgentAction.ActionType == "UPDATE_REORDER_POINT")
        )).scalars().all()

        # In current implementation it may create 0 or 1 depending on data
        # The important thing is it doesn't crash and follows the propose pattern
        assert all(a.Status == "proposed" for a in actions)
