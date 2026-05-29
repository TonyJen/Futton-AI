from app.api.routers.purchasing import get_supplier_pricing
from app.db.models import Item, ItemType, Supplier, SupplierItem, UnitOfMeasure


class TestPurchasingRouter:
    async def test_supplier_items_returns_item_metadata(self, db_session):
        supplier = Supplier(SupplierCode="SUP-TEST", SupplierName="Test Supplier", IsActive=True)
        item_type = ItemType(TypeCode="RAW", TypeName="Raw Material")
        unit = UnitOfMeasure(UnitCode="EA", UnitName="Each")
        db_session.add_all([supplier, item_type, unit])
        await db_session.flush()

        item = Item(
            ItemCode="ITEM-001",
            ItemName="Test Item",
            ItemTypeID=item_type.ItemTypeID,
            UnitID=unit.UnitID,
        )
        db_session.add(item)
        await db_session.flush()

        supplier_item = SupplierItem(
            SupplierID=supplier.SupplierID,
            ItemID=item.ItemID,
            UnitPrice=12.5,
            MinimumOrderQuantity=5,
            LeadTimeDays=7,
            IsPreferred=True,
        )
        db_session.add(supplier_item)
        await db_session.commit()

        data = await get_supplier_pricing(supplier.SupplierID, db_session)

        assert len(data) == 1
        assert data[0]["itemId"] == item.ItemID
        assert data[0]["itemCode"] == "ITEM-001"
        assert data[0]["itemName"] == "Test Item"
        assert data[0]["unitPrice"] == 12.5
