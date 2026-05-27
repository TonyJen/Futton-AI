"""
Tests for the manufacturing tools used by agents.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.tools import (
    find_low_stock_and_shortages,
    get_item_inventory_status,
    explode_bill_of_materials,
    run_abc_analysis,
)


@pytest.mark.asyncio
class TestManufacturingTools:
    async def test_find_low_stock_and_shortages_returns_list(self, db_session: AsyncSession):
        # Should not raise even on empty database
        results = await find_low_stock_and_shortages(db_session)
        assert isinstance(results, list)

    async def test_get_item_inventory_status(self, db_session: AsyncSession):
        # Should not raise even for non-existent item
        result = await get_item_inventory_status(db_session, item_id=999999)
        assert result["item_id"] == 999999
        assert "total_available" in result

    async def test_explode_bill_of_materials(self, db_session: AsyncSession):
        # Try exploding a finished good
        result = await explode_bill_of_materials(db_session, item_id=12, quantity=2)
        assert result["item_id"] == 12
        assert "components" in result

    async def test_run_abc_analysis(self, db_session: AsyncSession):
        result = await run_abc_analysis(db_session)
        assert isinstance(result, list)
