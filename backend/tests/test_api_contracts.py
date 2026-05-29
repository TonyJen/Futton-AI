import pytest
from uuid import uuid4

from app.api.routers.dashboard import (
    get_dashboard_kpis,
    get_inventory_distribution,
    get_production_trend,
)
from app.api.routers.inventory import list_inventory
from app.api.routers.items import list_items
from app.api.routers.sales import get_sales_summary
from app.db.models import (
    AgentAction,
    Customer,
    Inventory,
    Item,
    ItemType,
    SalesOrder,
    SalesQuote,
    UnitOfMeasure,
    Warehouse,
    WorkCenter,
    ProductionOrder,
)


async def seed_catalog(db_session):
    suffix = uuid4().hex[:6].upper()
    unit = UnitOfMeasure(UnitCode=f"EA{suffix}", UnitName="Each")
    raw_type = ItemType(TypeCode=f"RAW{suffix}", TypeName="Raw Material")
    finished_type = ItemType(TypeCode=f"FG{suffix}", TypeName="Finished Good")
    warehouse = Warehouse(WarehouseCode=f"MAIN{suffix}", WarehouseName="Main Plant", IsActive=True)
    db_session.add_all([unit, raw_type, finished_type, warehouse])
    await db_session.flush()

    raw_item = Item(
        ItemCode=f"RM-{suffix}",
        ItemName="Foam Roll",
        ItemTypeID=raw_type.ItemTypeID,
        UnitID=unit.UnitID,
        StandardCost=14.5,
        ReorderPoint=20,
        IsActive=True,
    )
    finished_item = Item(
        ItemCode=f"FG-{suffix}",
        ItemName="Classic Futon",
        ItemTypeID=finished_type.ItemTypeID,
        UnitID=unit.UnitID,
        StandardCost=199,
        ListPrice=349,
        IsActive=True,
    )
    db_session.add_all([raw_item, finished_item])
    await db_session.flush()

    db_session.add(
        Inventory(
            ItemID=raw_item.ItemID,
            WarehouseID=warehouse.WarehouseID,
            QuantityOnHand=12,
            QuantityAllocated=2,
        )
    )
    await db_session.commit()
    return {
        "unit": unit,
        "warehouse": warehouse,
        "raw_item": raw_item,
        "finished_item": finished_item,
        "suffix": suffix,
    }


class TestAPIContracts:
    async def test_items_endpoint_returns_camel_case_contract(self, db_session):
        seeded = await seed_catalog(db_session)

        data = await list_items(
            db=db_session,
            item_type=None,
            is_active=True,
            search=seeded["finished_item"].ItemCode,
            limit=100,
        )
        assert len(data) == 1
        assert data[0]["itemId"] == seeded["finished_item"].ItemID
        assert data[0]["itemCode"] == seeded["finished_item"].ItemCode
        assert data[0]["itemName"] == "Classic Futon"
        assert data[0]["itemType"] == seeded["finished_item"].item_type.TypeCode
        assert data[0]["standardCost"] == 199.0
        assert data[0]["listPrice"] == 349.0
        assert data[0]["isActive"] is True

    async def test_inventory_endpoint_returns_expected_fields(self, db_session):
        seeded = await seed_catalog(db_session)

        records = await list_inventory(db_session)
        first = next(item for item in records if item["itemCode"] == seeded["raw_item"].ItemCode)
        assert first["itemId"] == seeded["raw_item"].ItemID
        assert first["itemCode"] == seeded["raw_item"].ItemCode
        assert first["itemName"] == "Foam Roll"
        assert first["quantityOnHand"] == 12
        assert first["quantityAllocated"] == 2
        assert first["available"] == 10

    async def test_dashboard_endpoints_return_chart_ready_shapes(self, db_session):
        seeded = await seed_catalog(db_session)
        suffix = seeded["suffix"]
        work_center = WorkCenter(
            WorkCenterCode=f"CUT-{suffix}",
            WorkCenterName="Cutting",
            Capacity=100,
            IsActive=True,
        )
        db_session.add(work_center)
        await db_session.flush()

        db_session.add(
            ProductionOrder(
                WorkOrderNumber=f"WO-{suffix}",
                ItemID=seeded["finished_item"].ItemID,
                WarehouseID=seeded["warehouse"].WarehouseID,
                WorkCenterID=work_center.WorkCenterID,
                OrderQuantity=8,
                QuantityCompleted=3,
                PlannedCompletionDate="2026-05-29",
                ActualCompletionDate="2026-05-29",
                Status="InProgress",
            )
        )
        db_session.add(
            AgentAction(
                ActionType="purchase_order",
                ProposedPayloadJson="{}",
                Status="proposed",
            )
        )
        await db_session.commit()

        kpis = await get_dashboard_kpis(db_session)
        assert kpis["totalSkus"] >= 2
        assert kpis["lowStockItems"] >= 1
        assert kpis["pendingRecommendations"] >= 1

        distribution = await get_inventory_distribution(db_session)
        assert distribution[0]["name"]
        assert "fill" in distribution[0]

        trend = await get_production_trend(db_session)
        assert len(trend) == 7
        assert {"day", "planned", "completed"} <= set(trend[0].keys())

    async def test_sales_summary_endpoint_returns_expected_totals(self, db_session):
        seeded = await seed_catalog(db_session)
        suffix = seeded["suffix"]
        customer = Customer(
            CustomerCode=f"CUST-{suffix}",
            CustomerName="Acme Retail",
            CustomerType="Retail",
            IsActive=True,
        )
        db_session.add(customer)
        await db_session.flush()

        db_session.add(
            SalesOrder(
                OrderNumber=f"SO-{suffix}",
                CustomerID=customer.CustomerID,
                WarehouseID=seeded["warehouse"].WarehouseID,
                OrderDate="2026-05-20",
                TotalAmount=1250,
                Status="Confirmed",
            )
        )
        db_session.add(
            SalesQuote(
                QuoteNumber=f"QT-{suffix}",
                CustomerID=customer.CustomerID,
                QuoteDate="2026-05-20",
                Status="Sent",
                TotalAmount=400,
            )
        )
        await db_session.commit()

        payload = await get_sales_summary(db_session)
        assert payload["totalRevenueMTD"] == 1250.0
        assert payload["openQuotes"] == 1
        assert payload["avgOrderValue"] > 0
