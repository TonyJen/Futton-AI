"""
Sales & CRM Pydantic Schemas (Phase 2)
"""

from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import BaseModel

# =============================================================================
# CUSTOMER (extended)
# =============================================================================

class CustomerBase(BaseModel):
    CustomerCode: str
    CustomerName: str
    ContactName: Optional[str] = None
    Email: Optional[str] = None
    Phone: Optional[str] = None
    Address: Optional[str] = None
    City: Optional[str] = None
    State: Optional[str] = None
    ZipCode: Optional[str] = None
    Country: Optional[str] = None
    CreditLimit: Optional[float] = None
    CustomerType: str = "Retail"


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    CustomerID: int
    IsActive: bool

    class Config:
        from_attributes = True


# =============================================================================
# SALES QUOTE
# =============================================================================

class SalesQuoteDetailBase(BaseModel):
    LineNumber: int
    ItemID: int
    Quantity: float
    UnitPrice: float
    DiscountPercent: float = 0.0


class SalesQuoteDetailRead(SalesQuoteDetailBase):
    QuoteDetailID: int
    LineTotal: Optional[float] = None
    ItemCode: Optional[str] = None
    ItemName: Optional[str] = None

    class Config:
        from_attributes = True


class SalesQuoteBase(BaseModel):
    CustomerID: int
    SalesChannelID: Optional[int] = None
    SalesRepID: Optional[int] = None
    ExpirationDate: Optional[date] = None
    Notes: Optional[str] = None


class SalesQuoteCreate(SalesQuoteBase):
    details: List[SalesQuoteDetailBase]


class SalesQuoteRead(SalesQuoteBase):
    QuoteID: int
    QuoteNumber: str
    QuoteDate: date
    Status: str
    Subtotal: float
    DiscountAmount: float
    TaxAmount: float
    TotalAmount: float
    ConvertedToOrderID: Optional[int] = None
    CustomerName: Optional[str] = None

    class Config:
        from_attributes = True


class SalesQuoteDetailReadFull(SalesQuoteRead):
    details: List[SalesQuoteDetailRead] = []
    CustomerName: Optional[str] = None


# =============================================================================
# SALES RETURN
# =============================================================================

class SalesReturnDetailBase(BaseModel):
    SODetailID: int
    ItemID: int
    QuantityReturned: float
    UnitPrice: float
    RefundAmount: float
    Disposition: Optional[str] = None


class SalesReturnBase(BaseModel):
    SalesOrderID: int
    CustomerID: int
    ReturnReasonID: int
    Notes: Optional[str] = None


class SalesReturnCreate(SalesReturnBase):
    details: List[SalesReturnDetailBase]


class SalesReturnRead(SalesReturnBase):
    ReturnID: int
    ReturnNumber: str
    ReturnDate: date
    Status: str
    RefundAmount: float
    RestockingFee: float
    ApprovedBy: Optional[str] = None
    CustomerName: Optional[str] = None
    OrderNumber: Optional[str] = None

    class Config:
        from_attributes = True


# =============================================================================
# SALES REP & TERRITORY (basic)
# =============================================================================

class SalesRepRead(BaseModel):
    SalesRepID: int
    EmployeeCode: str
    FirstName: str
    LastName: str
    Email: Optional[str] = None
    IsActive: bool

    class Config:
        from_attributes = True


# =============================================================================
# SALES ORDER (kept for compatibility with existing Phase 1 router code)
# =============================================================================

class SalesOrderDetailBase(BaseModel):
    LineNumber: int
    ItemID: int
    Quantity: float
    UnitPrice: float
    DiscountPercent: float = 0.0


class SalesOrderDetailRead(SalesOrderDetailBase):
    SODetailID: int
    ItemCode: Optional[str] = None
    ItemName: Optional[str] = None

    class Config:
        from_attributes = True


class SalesOrderCreate(BaseModel):
    CustomerID: int
    WarehouseID: int
    SalesChannelID: Optional[int] = None
    OrderDate: Optional[str] = None
    RequestedDeliveryDate: Optional[str] = None
    TaxAmount: float = 0.0
    ShippingAmount: float = 0.0
    DiscountAmount: float = 0.0
    Notes: Optional[str] = None
    CreatedBy: Optional[str] = None
    details: List[SalesOrderDetailBase]


class SalesOrderRead(BaseModel):
    SalesOrderID: int
    OrderNumber: str
    Status: str
    TotalAmount: float
    CustomerID: Optional[int] = None
    CustomerName: Optional[str] = None

    class Config:
        from_attributes = True


class SalesOrderUpdate(BaseModel):
    Status: Optional[str] = None
    Notes: Optional[str] = None


class SalesOrderDetailReadFull(SalesOrderRead):
    CustomerName: Optional[str] = None
    WarehouseName: Optional[str] = None
    details: List[SalesOrderDetailRead] = []

    class Config:
        from_attributes = True
