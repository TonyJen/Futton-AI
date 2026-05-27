"""
Purchasing & Procurement Pydantic Schemas (Phase 3)
Suppliers, Supplier Items (pricing), Purchase Orders, Receiving
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import date


# =============================================================================
# SUPPLIER
# =============================================================================

class SupplierBase(BaseModel):
    SupplierCode: str
    SupplierName: str
    ContactName: Optional[str] = None
    Email: Optional[str] = None
    Phone: Optional[str] = None
    Address: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    ZipCode: Optional[str] = None
    Country: Optional[str] = None
    PaymentTerms: Optional[str] = None
    Rating: Optional[float] = Field(default=None, ge=0, le=5)


class SupplierCreate(SupplierBase):
    pass


class SupplierRead(SupplierBase):
    SupplierID: int
    IsActive: bool

    model_config = {"from_attributes": True}


# =============================================================================
# SUPPLIER ITEM (pricing / lead time matrix)
# =============================================================================

class SupplierItemBase(BaseModel):
    ItemID: int
    SupplierPartNumber: Optional[str] = None
    UnitPrice: float
    MinimumOrderQuantity: float = 1.0
    LeadTimeDays: int = 0
    IsPreferred: bool = False


class SupplierItemRead(SupplierItemBase):
    SupplierItemID: int
    SupplierID: int

    model_config = {"from_attributes": True}


class SupplierItemWithItem(SupplierItemRead):
    ItemCode: Optional[str] = None
    ItemName: Optional[str] = None


# =============================================================================
# PURCHASE ORDER DETAIL
# =============================================================================

class PurchaseOrderDetailBase(BaseModel):
    LineNumber: int
    ItemID: int
    Quantity: float
    UnitPrice: float


class PurchaseOrderDetailCreate(PurchaseOrderDetailBase):
    pass


class PurchaseOrderDetailRead(PurchaseOrderDetailBase):
    PODetailID: int
    QuantityReceived: float = 0.0
    LineTotal: Optional[float] = None

    model_config = {"from_attributes": True}


# =============================================================================
# PURCHASE ORDER
# =============================================================================

class PurchaseOrderBase(BaseModel):
    SupplierID: int
    WarehouseID: int = 1
    ExpectedDeliveryDate: Optional[date] = None
    Notes: Optional[str] = None


class PurchaseOrderCreate(PurchaseOrderBase):
    details: List[PurchaseOrderDetailCreate]


class PurchaseOrderRead(PurchaseOrderBase):
    PurchaseOrderID: int
    PONumber: str
    OrderDate: date
    Status: str  # Draft, Sent, Partial, Received, Cancelled
    Subtotal: float
    TaxAmount: float
    ShippingAmount: float
    TotalAmount: float
    CreatedBy: Optional[str] = None

    model_config = {"from_attributes": True}


class PurchaseOrderDetailReadFull(PurchaseOrderRead):
    details: List[PurchaseOrderDetailRead] = []
    SupplierName: Optional[str] = None
    WarehouseName: Optional[str] = None


# =============================================================================
# RECEIVING
# =============================================================================

class ReceiveLine(BaseModel):
    PODetailID: int
    QuantityReceived: float


class ReceiveGoodsPayload(BaseModel):
    lines: List[ReceiveLine]
    received_by: Optional[str] = "Receiving Clerk"
    notes: Optional[str] = None
