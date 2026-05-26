"""
Pydantic schemas for Inventory, Warehouses and Transactions.
"""

from typing import List, Optional

from pydantic import Field

from .common import BaseSchema, TimestampSchema


class WarehouseBase(BaseSchema):
    WarehouseCode: str = Field(..., max_length=20)
    WarehouseName: str = Field(..., max_length=100)
    Address: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    ZipCode: Optional[str] = None
    IsActive: bool = True


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseRead(WarehouseBase):
    WarehouseID: int


class InventoryBase(BaseSchema):
    ItemID: int
    WarehouseID: int
    QuantityOnHand: float = 0.0
    QuantityAllocated: float = 0.0


class InventoryRead(InventoryBase, TimestampSchema):
    InventoryID: int
    QuantityAvailable: float = Field(0.0, description="QuantityOnHand - QuantityAllocated (computed)")


class InventoryWithDetailsRead(InventoryRead):
    ItemCode: Optional[str] = None
    ItemName: Optional[str] = None
    WarehouseCode: Optional[str] = None
    WarehouseName: Optional[str] = None


class InventoryTransactionBase(BaseSchema):
    ItemID: int
    WarehouseID: int
    TransactionTypeID: int
    Quantity: float
    UnitCost: Optional[float] = None
    ReferenceNumber: Optional[str] = None
    ReferenceType: Optional[str] = None
    Notes: Optional[str] = None
    CreatedBy: Optional[str] = None


class InventoryTransactionCreate(InventoryTransactionBase):
    pass


class InventoryTransactionRead(InventoryTransactionBase, TimestampSchema):
    TransactionID: int
    TransactionDate: Optional[str] = None


class InventoryAdjustmentRequest(BaseSchema):
    """Simple request body for manual inventory adjustments."""
    ItemID: int
    WarehouseID: int
    QuantityChange: float  # positive or negative
    Reason: str
    ReferenceNumber: Optional[str] = "ADJ-MANUAL"
    CreatedBy: str = "api_user"
