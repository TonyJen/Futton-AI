"""
Purchasing Router (Phase 3)

Suppliers, Purchase Orders, Receiving workflow.
Mirrors the structure and quality of the Sales router.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_db
from app.schemas.purchasing import (
    PurchaseOrderCreate,
    PurchaseOrderDetailReadFull,
    PurchaseOrderRead,
    ReceiveGoodsPayload,
    SupplierRead,
)
from app.services.purchasing_service import (
    create_purchase_order,
    get_purchase_order,
    list_purchase_orders,
    list_suppliers,
    receive_goods,
)

router = APIRouter(prefix="/purchasing", tags=["Purchasing"])


def _serialize_supplier_item(si):
    item = si.item
    return {
        "supplierItemId": si.SupplierItemID,
        "itemId": si.ItemID,
        "itemCode": item.ItemCode if item else None,
        "itemName": item.ItemName if item else None,
        "unitPrice": si.UnitPrice,
        "minimumOrderQuantity": si.MinimumOrderQuantity,
        "leadTimeDays": si.LeadTimeDays,
        "isPreferred": si.IsPreferred,
    }


# Suppliers
@router.get("/suppliers", response_model=List[SupplierRead])
async def list_all_suppliers(active_only: bool = True, db=Depends(get_db)):
    suppliers = await list_suppliers(db, active_only=active_only)
    return [SupplierRead.model_validate(s) for s in suppliers]


@router.get("/suppliers/{supplier_id}/items")
async def get_supplier_pricing(supplier_id: int, db=Depends(get_db)):
    """Returns pricing / lead time data for a supplier (used by agents and UI)."""
    from app.services.purchasing_service import get_supplier_items

    items = await get_supplier_items(db, supplier_id)
    return [_serialize_supplier_item(si) for si in items]


# Purchase Orders
@router.post("/purchase-orders", response_model=PurchaseOrderRead, status_code=status.HTTP_201_CREATED)
async def create_po(payload: PurchaseOrderCreate, db=Depends(get_db)):
    try:
        po = await create_purchase_order(db, payload.model_dump())
        return PurchaseOrderRead.model_validate(po)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/purchase-orders", response_model=List[PurchaseOrderRead])
async def list_pos(status: Optional[str] = None, db=Depends(get_db)):
    pos = await list_purchase_orders(db, status=status)
    dtos = []
    for po in pos:
        dto = PurchaseOrderRead.model_validate(po)
        if po.supplier:
            dto.SupplierName = po.supplier.SupplierName
        dtos.append(dto)
    return dtos


@router.get("/purchase-orders/{po_id}", response_model=PurchaseOrderDetailReadFull)
async def get_po(po_id: int, db=Depends(get_db)):
    po = await get_purchase_order(db, po_id)
    if not po:
        raise HTTPException(404, "Purchase Order not found")

    dto = PurchaseOrderDetailReadFull.model_validate(po)
    if po.supplier:
        dto.SupplierName = po.supplier.SupplierName
    if po.warehouse:
        dto.WarehouseName = po.warehouse.WarehouseName
    for detail_dto, detail_model in zip(dto.details, po.details):
        if detail_model.item:
            detail_dto.ItemCode = detail_model.item.ItemCode
            detail_dto.ItemName = detail_model.item.ItemName
    return dto


@router.post("/purchase-orders/{po_id}/receive")
async def receive_po(po_id: int, payload: ReceiveGoodsPayload, db=Depends(get_db)):
    try:
        result = await receive_goods(db, po_id, payload.model_dump())
        return result
    except Exception as e:
        raise HTTPException(400, str(e))
