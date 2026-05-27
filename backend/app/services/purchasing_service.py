"""
Purchasing Service Layer (Phase 3)

Core operations for:
- Suppliers
- Purchase Order creation (rich, from agent proposals or manual)
- Goods receiving (updates PO + creates inventory transactions)
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    Supplier,
    SupplierItem,
    PurchaseOrder,
    PurchaseOrderDetail,
    Item,
    Inventory,
    InventoryTransaction,
)


# =============================================================================
# SUPPLIERS
# =============================================================================

async def list_suppliers(db: AsyncSession, active_only: bool = True) -> List[Supplier]:
    stmt = select(Supplier)
    if active_only:
        stmt = stmt.where(Supplier.IsActive.is_(True))
    stmt = stmt.order_by(Supplier.SupplierName)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_supplier(db: AsyncSession, supplier_id: int) -> Optional[Supplier]:
    return await db.get(Supplier, supplier_id)


async def get_supplier_items(db: AsyncSession, supplier_id: int) -> List[SupplierItem]:
    stmt = (
        select(SupplierItem)
        .where(SupplierItem.SupplierID == supplier_id)
        .options(selectinload(SupplierItem.item))
        .order_by(SupplierItem.IsPreferred.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


# =============================================================================
# PURCHASE ORDERS
# =============================================================================

async def create_purchase_order(db: AsyncSession, payload: Dict[str, Any]) -> PurchaseOrder:
    """
    Create a Purchase Order with details.
    Supports both manual UI creation and agent-proposed actions.
    """
    po_data = {k: v for k, v in payload.items() if k != "details"}

    # Generate PO Number
    year = datetime.now().year
    count_stmt = select(PurchaseOrder).where(PurchaseOrder.OrderDate.like(f"{year}-%"))
    count = len((await db.execute(count_stmt)).scalars().all()) + 1
    po_number = f"PO-{year}-{count:04d}"

    po = PurchaseOrder(
        PONumber=po_number,
        OrderDate=datetime.now().strftime("%Y-%m-%d"),
        Status="Draft",
        **po_data,
    )
    db.add(po)
    await db.flush()

    subtotal = 0.0
    for i, detail in enumerate(payload.get("details", []), 1):
        item = await db.get(Item, detail["ItemID"])
        if not item:
            raise ValueError(f"Item {detail['ItemID']} not found")

        unit_price = detail.get("UnitPrice") or getattr(item, "standardCost", 0) or 0
        qty = detail.get("Quantity", 0)

        line = PurchaseOrderDetail(
            PurchaseOrderID=po.PurchaseOrderID,
            LineNumber=i,
            ItemID=detail["ItemID"],
            Quantity=qty,
            UnitPrice=unit_price,
            QuantityReceived=0.0,
        )
        db.add(line)
        subtotal += qty * unit_price

    po.Subtotal = subtotal
    po.TotalAmount = subtotal + po.TaxAmount + po.ShippingAmount

    await db.flush()
    await db.refresh(po)
    return po


async def list_purchase_orders(db: AsyncSession, status: Optional[str] = None) -> List[PurchaseOrder]:
    stmt = select(PurchaseOrder).order_by(PurchaseOrder.PurchaseOrderID.desc())
    if status:
        stmt = stmt.where(PurchaseOrder.Status == status)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_purchase_order(db: AsyncSession, po_id: int) -> Optional[PurchaseOrder]:
    stmt = (
        select(PurchaseOrder)
        .where(PurchaseOrder.PurchaseOrderID == po_id)
        .options(
            selectinload(PurchaseOrder.details).selectinload(PurchaseOrderDetail.item),
            selectinload(PurchaseOrder.supplier),
            selectinload(PurchaseOrder.warehouse),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def receive_goods(
    db: AsyncSession, po_id: int, payload: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process receiving for a PO.
    Updates QuantityReceived on lines, changes PO status, creates Inventory + Transactions.
    """
    po = await get_purchase_order(db, po_id)
    if not po:
        raise ValueError("Purchase Order not found")

    received_by = payload.get("received_by", "System")
    lines_received = payload.get("lines", [])

    total_received_value = 0.0

    for line_data in lines_received:
        podetail_id = line_data["PODetailID"]
        qty = float(line_data["QuantityReceived"])

        # Find the matching detail
        detail = next((d for d in po.details if d.PODetailID == podetail_id), None)
        if not detail:
            continue

        # Update received qty (cap at ordered qty)
        new_received = min(detail.QuantityReceived + qty, detail.Quantity)
        delta = new_received - detail.QuantityReceived
        detail.QuantityReceived = new_received

        if delta > 0:
            # Update inventory
            inv_stmt = select(Inventory).where(
                (Inventory.ItemID == detail.ItemID) &
                (Inventory.WarehouseID == po.WarehouseID)
            )
            inv = (await db.execute(inv_stmt)).scalar_one_or_none()

            if not inv:
                inv = Inventory(
                    ItemID=detail.ItemID,
                    WarehouseID=po.WarehouseID,
                    QuantityOnHand=0,
                )
                db.add(inv)
                await db.flush()

            inv.QuantityOnHand = (inv.QuantityOnHand or 0) + delta

            # Create transaction
            tx = InventoryTransaction(
                ItemID=detail.ItemID,
                WarehouseID=po.WarehouseID,
                TransactionType="Receipt",
                Quantity=delta,
                UnitCost=detail.UnitPrice,
                ReferenceNumber=po.PONumber,
                Notes=f"PO Receiving - {received_by}",
                CreatedBy=received_by,
            )
            db.add(tx)

            total_received_value += delta * detail.UnitPrice

    # Update PO status
    all_received = all(d.QuantityReceived >= d.Quantity for d in po.details)
    any_received = any(d.QuantityReceived > 0 for d in po.details)

    if all_received:
        po.Status = "Received"
        po.ActualDeliveryDate = datetime.now().strftime("%Y-%m-%d")
    elif any_received:
        po.Status = "Partial"

    await db.flush()

    return {
        "success": True,
        "purchase_order_id": po.PurchaseOrderID,
        "status": po.Status,
        "value_received": total_received_value,
        "message": f"Receiving recorded for {po.PONumber}",
    }
