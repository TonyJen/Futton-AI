"""
Clean test script for the AI agents (now that package __init__.py files are restored).
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.agents.mrp_agent import MRPPlanningAgent
from app.agents.inventory_agent import InventoryIntelligenceAgent


async def test_mrp_agent():
    print("\n=== Testing MRP Planning Agent ===")
    engine = create_async_engine("sqlite+aiosqlite:///./data/futon_manufacturing.db", echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with AsyncSessionLocal() as db:
        agent = MRPPlanningAgent(db)
        result = await agent.run({"item_id": 12, "quantity": 4})

        print(f"Proposals created: {result.get('proposals_created')}")
        print("Reasoning:")
        for step in result.get("reasoning_trace", []):
            print(f"  - {step}")

    await engine.dispose()


async def test_inventory_agent():
    print("\n=== Testing Inventory Intelligence Agent ===")
    engine = create_async_engine("sqlite+aiosqlite:///./data/futon_manufacturing.db", echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with AsyncSessionLocal() as db:
        agent = InventoryIntelligenceAgent(db)
        result = await agent.run({})

        print(f"Proposals created: {result.get('proposals_created')}")
        print("Reasoning:")
        for step in result.get("reasoning_trace", []):
            print(f"  - {step}")

    await engine.dispose()


async def main():
    await test_mrp_agent()
    await test_inventory_agent()
    print("\n=== All agent tests completed ===")


if __name__ == "__main__":
    asyncio.run(main())
