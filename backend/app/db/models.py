"""
SQLAlchemy 2.0 ORM models for Futon Manufacturing ERP.

Models are designed to closely match the consolidated SQLite schema
produced by the Wave 2 DB Agent (data/futon_manufacturing_sqlite.sql).

Uses modern declarative style with Mapped[] annotations.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    Index,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


# =============================================================================
# MIXIN / UTILITIES
# =============================================================================

class TimestampMixin:
    """Common audit timestamps (stored as TEXT in SQLite but mapped as DateTime)."""

    CreatedDate: Mapped[Optional[datetime]] = mapped_column(
        DateTime, server_default=func.now(), nullable=True
    )
    ModifiedDate: Mapped[Optional[datetime]] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=True
    )


# =============================================================================
# REFERENCE / LOOKUP TABLES
# =============================================================================


class UnitOfMeasure(Base):
    __tablename__ = "UnitOfMeasure"

    UnitID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    UnitCode: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    UnitName: Mapped[str] = mapped_column(String(50), nullable=False)
    Description: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    items: Mapped[List["Item"]] = relationship(back_populates="unit")
    bom_entries: Mapped[List["BillOfMaterial"]] = relationship(back_populates="unit")


class ItemType(Base):
    __tablename__ = "ItemType"

    ItemTypeID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    TypeCode: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    TypeName: Mapped[str] = mapped_column(String(100), nullable=False)
    Description: Mapped[Optional[str]] = mapped_column(Text)

    items: Mapped[List["Item"]] = relationship(back_populates="item_type")


class TransactionType(Base):
    __tablename__ = "TransactionType"

    TransactionTypeID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    TypeCode: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    TypeName: Mapped[str] = mapped_column(String(100), nullable=False)
    Description: Mapped[Optional[str]] = mapped_column(Text)

    inventory_transactions: Mapped[List["InventoryTransaction"]] = relationship(
        back_populates="transaction_type"
    )


class SalesChannel(Base):
    __tablename__ = "SalesChannel"

    SalesChannelID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ChannelCode: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    ChannelName: Mapped[str] = mapped_column(String(100), nullable=False)
    Description: Mapped[Optional[str]] = mapped_column(Text)
    IsActive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sales_orders: Mapped[List["SalesOrder"]] = relationship(back_populates="sales_channel")
    stores: Mapped[List["Store"]] = relationship(back_populates="sales_channel")


class Store(Base):
    __tablename__ = "Store"

    StoreID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    StoreCode: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    StoreName: Mapped[str] = mapped_column(String(100), nullable=False)
    SalesChannelID: Mapped[int] = mapped_column(ForeignKey("SalesChannel.SalesChannelID"), nullable=False)
    Manager: Mapped[Optional[str]] = mapped_column(String(100))
    Phone: Mapped[Optional[str]] = mapped_column(String(20))
    Email: Mapped[Optional[str]] = mapped_column(String(100))
    Address: Mapped[Optional[str]] = mapped_column(Text)
    City: Mapped[Optional[str]] = mapped_column(String(100))
    State: Mapped[Optional[str]] = mapped_column(String(50))
    ZipCode: Mapped[Optional[str]] = mapped_column(String(20))
    OpenDate: Mapped[Optional[str]] = mapped_column(String(10))
    IsActive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sales_channel: Mapped["SalesChannel"] = relationship(back_populates="stores")
    sales_orders: Mapped[List["SalesOrder"]] = relationship(back_populates="store")


# =============================================================================
# SALES REPS & TERRITORIES (Phase 2 CRM)
# =============================================================================

class SalesTerritory(Base):
    __tablename__ = "SalesTerritory"

    TerritoryID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    TerritoryCode: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    TerritoryName: Mapped[str] = mapped_column(String(100), nullable=False)
    Region: Mapped[Optional[str]] = mapped_column(String(50))
    IsActive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sales_reps: Mapped[List["SalesRep"]] = relationship(back_populates="territory")
    customers: Mapped[List["Customer"]] = relationship(back_populates="territory")


class SalesRep(Base):
    __tablename__ = "SalesRep"

    SalesRepID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    EmployeeCode: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    FirstName: Mapped[str] = mapped_column(String(50), nullable=False)
    LastName: Mapped[str] = mapped_column(String(50), nullable=False)
    Email: Mapped[Optional[str]] = mapped_column(String(100))
    Phone: Mapped[Optional[str]] = mapped_column(String(20))
    TerritoryID: Mapped[Optional[int]] = mapped_column(ForeignKey("SalesTerritory.TerritoryID"))
    HireDate: Mapped[Optional[str]] = mapped_column(String(10))
    IsActive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    territory: Mapped[Optional["SalesTerritory"]] = relationship(back_populates="sales_reps")
    customers: Mapped[List["Customer"]] = relationship(back_populates="sales_rep")
    sales_orders: Mapped[List["SalesOrder"]] = relationship(back_populates="sales_rep")
    quotes: Mapped[List["SalesQuote"]] = relationship(back_populates="sales_rep")


# =============================================================================
# CORE MASTER DATA
# =============================================================================


class Item(Base, TimestampMixin):
    __tablename__ = "Items"

    ItemID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ItemCode: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    ItemName: Mapped[str] = mapped_column(String(255), nullable=False)
    ItemTypeID: Mapped[int] = mapped_column(ForeignKey("ItemType.ItemTypeID"), nullable=False)
    UnitID: Mapped[int] = mapped_column(ForeignKey("UnitOfMeasure.UnitID"), nullable=False)

    Description: Mapped[Optional[str]] = mapped_column(Text)
    StandardCost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    ListPrice: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    IsActive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    LeadTimeDays: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    ReorderPoint: Mapped[float] = mapped_column(Float, default=0.0)
    SafetyStock: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    item_type: Mapped["ItemType"] = relationship(back_populates="items")
    unit: Mapped["UnitOfMeasure"] = relationship(back_populates="items")

    bom_as_parent: Mapped[List["BillOfMaterial"]] = relationship(
        foreign_keys="BillOfMaterial.ParentItemID", back_populates="parent_item"
    )
    bom_as_component: Mapped[List["BillOfMaterial"]] = relationship(
        foreign_keys="BillOfMaterial.ComponentItemID", back_populates="component_item"
    )

    inventory_records: Mapped[List["Inventory"]] = relationship(back_populates="item")
    production_orders: Mapped[List["ProductionOrder"]] = relationship(back_populates="item")
    sales_order_details: Mapped[List["SalesOrderDetail"]] = relationship(back_populates="item")


class BillOfMaterial(Base, TimestampMixin):
    """
    Multi-level Bill of Materials.
    Supports recursive structures for futon assemblies.
    """

    __tablename__ = "BillOfMaterials"

    BOMID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ParentItemID: Mapped[int] = mapped_column(ForeignKey("Items.ItemID"), nullable=False, index=True)
    ComponentItemID: Mapped[int] = mapped_column(
        ForeignKey("Items.ItemID"), nullable=False, index=True
    )
    Quantity: Mapped[float] = mapped_column(Float, nullable=False)
    UnitID: Mapped[int] = mapped_column(ForeignKey("UnitOfMeasure.UnitID"), nullable=False)

    ScrapRate: Mapped[float] = mapped_column(Float, default=0.0)  # percentage e.g. 0.05 = 5%
    EffectiveDate: Mapped[Optional[str]] = mapped_column(String(10))  # YYYY-MM-DD
    EndDate: Mapped[Optional[str]] = mapped_column(String(10))
    BOMLevel: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    IsActive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    Notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    parent_item: Mapped["Item"] = relationship(
        foreign_keys=[ParentItemID], back_populates="bom_as_parent"
    )
    component_item: Mapped["Item"] = relationship(
        foreign_keys=[ComponentItemID], back_populates="bom_as_component"
    )
    unit: Mapped["UnitOfMeasure"] = relationship(back_populates="bom_entries")

    __table_args__ = (
        # Prevent self-referencing BOMs at DB level
        UniqueConstraint("ParentItemID", "ComponentItemID", name="uq_bom_parent_component"),
    )


# Compatibility alias (many AI agent files expect BillOfMaterials)
BillOfMaterials = BillOfMaterial

# =============================================================================
# WAREHOUSE & INVENTORY
# =============================================================================


class Warehouse(Base):
    __tablename__ = "Warehouse"

    WarehouseID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    WarehouseCode: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    WarehouseName: Mapped[str] = mapped_column(String(100), nullable=False)
    Address: Mapped[Optional[str]] = mapped_column(Text)
    City: Mapped[Optional[str]] = mapped_column(String(100))
    State: Mapped[Optional[str]] = mapped_column(String(50))
    ZipCode: Mapped[Optional[str]] = mapped_column(String(20))
    IsActive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    inventory: Mapped[List["Inventory"]] = relationship(back_populates="warehouse")
    production_orders: Mapped[List["ProductionOrder"]] = relationship(back_populates="warehouse")
    sales_orders: Mapped[List["SalesOrder"]] = relationship(back_populates="warehouse")


class Inventory(Base):
    """
    Current inventory snapshot per item + warehouse.
    Note: SQLite version does not have persisted computed column for QuantityAvailable.
    Use the @property or service layer: QuantityOnHand - QuantityAllocated
    """

    __tablename__ = "Inventory"

    InventoryID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ItemID: Mapped[int] = mapped_column(ForeignKey("Items.ItemID"), nullable=False)
    WarehouseID: Mapped[int] = mapped_column(ForeignKey("Warehouse.WarehouseID"), nullable=False)

    QuantityOnHand: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    QuantityAllocated: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    LastCountDate: Mapped[Optional[str]] = mapped_column(String(20))
    LastUpdated: Mapped[Optional[datetime]] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    item: Mapped["Item"] = relationship(back_populates="inventory_records")
    warehouse: Mapped["Warehouse"] = relationship(back_populates="inventory")

    __table_args__ = (
        UniqueConstraint("ItemID", "WarehouseID", name="uq_inventory_item_warehouse"),
    )

    @property
    def quantity_available(self) -> float:
        """Calculated available inventory (not persisted)."""
        return self.QuantityOnHand - self.QuantityAllocated


class InventoryTransaction(Base):
    __tablename__ = "InventoryTransaction"

    TransactionID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ItemID: Mapped[int] = mapped_column(ForeignKey("Items.ItemID"), nullable=False, index=True)
    WarehouseID: Mapped[int] = mapped_column(ForeignKey("Warehouse.WarehouseID"), nullable=False)
    TransactionTypeID: Mapped[int] = mapped_column(
        ForeignKey("TransactionType.TransactionTypeID"), nullable=False
    )

    Quantity: Mapped[float] = mapped_column(Float, nullable=False)
    UnitCost: Mapped[Optional[float]] = mapped_column(Float)
    ReferenceNumber: Mapped[Optional[str]] = mapped_column(String(50))
    ReferenceType: Mapped[Optional[str]] = mapped_column(String(50))  # PO, SO, WO, ADJ
    Notes: Mapped[Optional[str]] = mapped_column(Text)
    TransactionDate: Mapped[Optional[datetime]] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )
    CreatedBy: Mapped[Optional[str]] = mapped_column(String(100))

    # Relationships
    item: Mapped["Item"] = relationship()
    warehouse: Mapped["Warehouse"] = relationship()
    transaction_type: Mapped["TransactionType"] = relationship(
        back_populates="inventory_transactions"
    )


# =============================================================================
# PRODUCTION
# =============================================================================


class WorkCenter(Base):
    __tablename__ = "WorkCenter"

    WorkCenterID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    WorkCenterCode: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    WorkCenterName: Mapped[str] = mapped_column(String(100), nullable=False)
    Description: Mapped[Optional[str]] = mapped_column(Text)
    Capacity: Mapped[Optional[float]] = mapped_column(Float)  # units per day
    IsActive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    production_orders: Mapped[List["ProductionOrder"]] = relationship(
        back_populates="work_center"
    )


class ProductionOrder(Base, TimestampMixin):
    __tablename__ = "ProductionOrder"

    ProductionOrderID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    WorkOrderNumber: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    ItemID: Mapped[int] = mapped_column(ForeignKey("Items.ItemID"), nullable=False)
    WarehouseID: Mapped[int] = mapped_column(ForeignKey("Warehouse.WarehouseID"), nullable=False)
    WorkCenterID: Mapped[Optional[int]] = mapped_column(ForeignKey("WorkCenter.WorkCenterID"))

    OrderQuantity: Mapped[float] = mapped_column(Float, nullable=False)
    QuantityCompleted: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    QuantityScrapped: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    StartDate: Mapped[Optional[str]] = mapped_column(String(10))
    PlannedCompletionDate: Mapped[Optional[str]] = mapped_column(String(10))
    ActualCompletionDate: Mapped[Optional[str]] = mapped_column(String(10))

    Status: Mapped[str] = mapped_column(String(20), default="Planned", nullable=False)  # Planned, Released, InProgress, Completed, Cancelled
    Priority: Mapped[int] = mapped_column(Integer, default=5)

    Notes: Mapped[Optional[str]] = mapped_column(Text)
    CreatedBy: Mapped[Optional[str]] = mapped_column(String(100))

    # Relationships
    item: Mapped["Item"] = relationship(back_populates="production_orders")
    warehouse: Mapped["Warehouse"] = relationship(back_populates="production_orders")
    work_center: Mapped[Optional["WorkCenter"]] = relationship(back_populates="production_orders")

    materials: Mapped[List["ProductionOrderMaterial"]] = relationship(
        back_populates="production_order", cascade="all, delete-orphan"
    )


class ProductionOrderMaterial(Base):
    __tablename__ = "ProductionOrderMaterial"

    ProdOrderMaterialID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ProductionOrderID: Mapped[int] = mapped_column(
        ForeignKey("ProductionOrder.ProductionOrderID"), nullable=False
    )
    ItemID: Mapped[int] = mapped_column(ForeignKey("Items.ItemID"), nullable=False)

    RequiredQuantity: Mapped[float] = mapped_column(Float, nullable=False)
    IssuedQuantity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    production_order: Mapped["ProductionOrder"] = relationship(back_populates="materials")
    item: Mapped["Item"] = relationship()


# =============================================================================
# CUSTOMERS & SALES (core Phase 1 entities)
# =============================================================================


class Customer(Base):
    __tablename__ = "Customer"

    CustomerID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    CustomerCode: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    CustomerName: Mapped[str] = mapped_column(String(255), nullable=False)
    ContactName: Mapped[Optional[str]] = mapped_column(String(100))
    Email: Mapped[Optional[str]] = mapped_column(String(100))
    Phone: Mapped[Optional[str]] = mapped_column(String(20))
    Address: Mapped[Optional[str]] = mapped_column(Text)
    City: Mapped[Optional[str]] = mapped_column(String(100))
    State: Mapped[Optional[str]] = mapped_column(String(50))
    ZipCode: Mapped[Optional[str]] = mapped_column(String(20))
    Country: Mapped[Optional[str]] = mapped_column(String(50))
    CreditLimit: Mapped[Optional[float]] = mapped_column(Float)
    CustomerType: Mapped[str] = mapped_column(String(20), default="Retail")
    SalesRepID: Mapped[Optional[int]] = mapped_column(ForeignKey("SalesRep.SalesRepID"))
    TerritoryID: Mapped[Optional[int]] = mapped_column(ForeignKey("SalesTerritory.TerritoryID"))
    IsActive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    CreatedDate: Mapped[Optional[datetime]] = mapped_column(
        DateTime, server_default=func.now(), nullable=True
    )

    sales_orders: Mapped[List["SalesOrder"]] = relationship(back_populates="customer")
    sales_rep: Mapped[Optional["SalesRep"]] = relationship(back_populates="customers")
    territory: Mapped[Optional["SalesTerritory"]] = relationship(back_populates="customers")
    quotes: Mapped[List["SalesQuote"]] = relationship(back_populates="customer")
    returns: Mapped[List["SalesReturn"]] = relationship(back_populates="customer")


class SalesOrder(Base, TimestampMixin):
    __tablename__ = "SalesOrder"

    SalesOrderID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    OrderNumber: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    CustomerID: Mapped[int] = mapped_column(ForeignKey("Customer.CustomerID"), nullable=False)
    WarehouseID: Mapped[int] = mapped_column(ForeignKey("Warehouse.WarehouseID"), nullable=False)
    SalesChannelID: Mapped[Optional[int]] = mapped_column(
        ForeignKey("SalesChannel.SalesChannelID")
    )
    StoreID: Mapped[Optional[int]] = mapped_column(ForeignKey("Store.StoreID"))
    SalesRepID: Mapped[Optional[int]] = mapped_column(ForeignKey("SalesRep.SalesRepID"))

    OrderDate: Mapped[str] = mapped_column(String(10), nullable=False, server_default=func.current_date())
    RequestedDeliveryDate: Mapped[Optional[str]] = mapped_column(String(10))
    ShipDate: Mapped[Optional[str]] = mapped_column(String(10))

    Status: Mapped[str] = mapped_column(
        String(20), default="Draft", nullable=False
    )  # Draft, Confirmed, InProduction, Shipped, Delivered, Cancelled

    Subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    TaxAmount: Mapped[float] = mapped_column(Float, default=0.0)
    ShippingAmount: Mapped[float] = mapped_column(Float, default=0.0)
    TotalAmount: Mapped[float] = mapped_column(Float, default=0.0)
    DiscountAmount: Mapped[float] = mapped_column(Float, default=0.0)

    Notes: Mapped[Optional[str]] = mapped_column(Text)
    CreatedBy: Mapped[Optional[str]] = mapped_column(String(100))

    # Relationships
    customer: Mapped["Customer"] = relationship(back_populates="sales_orders")
    warehouse: Mapped["Warehouse"] = relationship(back_populates="sales_orders")
    sales_channel: Mapped[Optional["SalesChannel"]] = relationship(back_populates="sales_orders")
    sales_rep: Mapped[Optional["SalesRep"]] = relationship(back_populates="sales_orders")
    store: Mapped[Optional["Store"]] = relationship(back_populates="sales_orders")
    quotes: Mapped[List["SalesQuote"]] = relationship(back_populates="converted_order")

    details: Mapped[List["SalesOrderDetail"]] = relationship(
        back_populates="sales_order", cascade="all, delete-orphan"
    )


class SalesOrderDetail(Base):
    __tablename__ = "SalesOrderDetail"

    SODetailID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    SalesOrderID: Mapped[int] = mapped_column(
        ForeignKey("SalesOrder.SalesOrderID"), nullable=False
    )
    LineNumber: Mapped[int] = mapped_column(Integer, nullable=False)
    ItemID: Mapped[int] = mapped_column(ForeignKey("Items.ItemID"), nullable=False)

    Quantity: Mapped[float] = mapped_column(Float, nullable=False)
    UnitPrice: Mapped[float] = mapped_column(Float, nullable=False)
    QuantityShipped: Mapped[float] = mapped_column(Float, default=0.0)
    DiscountPercent: Mapped[float] = mapped_column(Float, default=0.0)

    # Relationships
    sales_order: Mapped["SalesOrder"] = relationship(back_populates="details")
    item: Mapped["Item"] = relationship(back_populates="sales_order_details")

    @property
    def line_total(self) -> float:
        return self.Quantity * self.UnitPrice

    @property
    def net_amount(self) -> float:
        return self.line_total * (1 - self.DiscountPercent / 100)


# =============================================================================
# PHASE 2 SALES & CRM MODELS
# =============================================================================

class SalesQuote(Base):
    __tablename__ = "SalesQuote"

    QuoteID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    QuoteNumber: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    CustomerID: Mapped[int] = mapped_column(ForeignKey("Customer.CustomerID"), nullable=False)
    SalesChannelID: Mapped[Optional[int]] = mapped_column(ForeignKey("SalesChannel.SalesChannelID"))
    SalesRepID: Mapped[Optional[int]] = mapped_column(ForeignKey("SalesRep.SalesRepID"))

    QuoteDate: Mapped[str] = mapped_column(String(10), nullable=False, server_default=func.current_date())
    ExpirationDate: Mapped[Optional[str]] = mapped_column(String(10))
    Status: Mapped[str] = mapped_column(String(20), default="Draft", nullable=False)  # Draft, Sent, Accepted, Declined, Expired

    Subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    DiscountAmount: Mapped[float] = mapped_column(Float, default=0.0)
    TaxAmount: Mapped[float] = mapped_column(Float, default=0.0)
    TotalAmount: Mapped[float] = mapped_column(Float, default=0.0)

    ConvertedToOrderID: Mapped[Optional[int]] = mapped_column(ForeignKey("SalesOrder.SalesOrderID"))
    Notes: Mapped[Optional[str]] = mapped_column(Text)
    CreatedBy: Mapped[Optional[str]] = mapped_column(String(100))
    CreatedDate: Mapped[Optional[datetime]] = mapped_column(
        DateTime, server_default=func.now(), nullable=True
    )

    customer: Mapped["Customer"] = relationship(back_populates="quotes")
    sales_channel: Mapped[Optional["SalesChannel"]] = relationship()
    sales_rep: Mapped[Optional["SalesRep"]] = relationship(back_populates="quotes")
    converted_order: Mapped[Optional["SalesOrder"]] = relationship()

    details: Mapped[List["SalesQuoteDetail"]] = relationship(
        back_populates="quote", cascade="all, delete-orphan"
    )


class SalesQuoteDetail(Base):
    __tablename__ = "SalesQuoteDetail"

    QuoteDetailID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    QuoteID: Mapped[int] = mapped_column(ForeignKey("SalesQuote.QuoteID"), nullable=False)
    LineNumber: Mapped[int] = mapped_column(Integer, nullable=False)
    ItemID: Mapped[int] = mapped_column(ForeignKey("Items.ItemID"), nullable=False)

    Quantity: Mapped[float] = mapped_column(Float, nullable=False)
    UnitPrice: Mapped[float] = mapped_column(Float, nullable=False)
    DiscountPercent: Mapped[float] = mapped_column(Float, default=0.0)

    quote: Mapped["SalesQuote"] = relationship(back_populates="details")
    item: Mapped["Item"] = relationship()


class SalesReturn(Base):
    __tablename__ = "SalesReturn"

    ReturnID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ReturnNumber: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    SalesOrderID: Mapped[int] = mapped_column(ForeignKey("SalesOrder.SalesOrderID"), nullable=False)
    CustomerID: Mapped[int] = mapped_column(ForeignKey("Customer.CustomerID"), nullable=False)
    ReturnReasonID: Mapped[int] = mapped_column(ForeignKey("ReturnReason.ReturnReasonID"), nullable=False)

    ReturnDate: Mapped[str] = mapped_column(String(10), nullable=False, server_default=func.current_date())
    Status: Mapped[str] = mapped_column(String(20), default="Pending", nullable=False)  # Pending, Approved, Received, Refunded, Denied

    RefundAmount: Mapped[float] = mapped_column(Float, default=0.0)
    RestockingFee: Mapped[float] = mapped_column(Float, default=0.0)
    Notes: Mapped[Optional[str]] = mapped_column(Text)
    ApprovedBy: Mapped[Optional[str]] = mapped_column(String(100))
    ApprovedDate: Mapped[Optional[str]] = mapped_column(String(30))
    CreatedDate: Mapped[Optional[datetime]] = mapped_column(
        DateTime, server_default=func.now(), nullable=True
    )

    sales_order: Mapped["SalesOrder"] = relationship()
    customer: Mapped["Customer"] = relationship(back_populates="returns")
    return_reason: Mapped["ReturnReason"] = relationship()

    details: Mapped[List["SalesReturnDetail"]] = relationship(
        back_populates="sales_return", cascade="all, delete-orphan"
    )


class SalesReturnDetail(Base):
    __tablename__ = "SalesReturnDetail"

    ReturnDetailID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ReturnID: Mapped[int] = mapped_column(ForeignKey("SalesReturn.ReturnID"), nullable=False)
    SODetailID: Mapped[int] = mapped_column(ForeignKey("SalesOrderDetail.SODetailID"), nullable=False)
    ItemID: Mapped[int] = mapped_column(ForeignKey("Items.ItemID"), nullable=False)

    QuantityReturned: Mapped[float] = mapped_column(Float, nullable=False)
    UnitPrice: Mapped[float] = mapped_column(Float, nullable=False)
    RefundAmount: Mapped[float] = mapped_column(Float, nullable=False)
    Disposition: Mapped[Optional[str]] = mapped_column(String(50))  # Restock, Scrap, Repair, RMA

    sales_return: Mapped["SalesReturn"] = relationship(back_populates="details")
    sales_order_detail: Mapped["SalesOrderDetail"] = relationship()
    item: Mapped["Item"] = relationship()


# =============================================================================
# AGENT TABLES (for future LangGraph integration - included for schema completeness)
# =============================================================================


class AgentConversation(Base):
    __tablename__ = "AgentConversation"

    ConversationID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    AgentName: Mapped[str] = mapped_column(String(100), nullable=False)
    SessionId: Mapped[Optional[str]] = mapped_column(String(100))
    UserId: Mapped[Optional[str]] = mapped_column(String(100))
    Title: Mapped[Optional[str]] = mapped_column(Text)
    StartedAt: Mapped[str] = mapped_column(String(30), server_default=func.now())
    LastMessageAt: Mapped[Optional[str]] = mapped_column(String(30))
    Status: Mapped[str] = mapped_column(String(20), default="active")
    MetadataJson: Mapped[Optional[str]] = mapped_column(Text)

    actions: Mapped[List["AgentAction"]] = relationship(back_populates="conversation")
    recommendations: Mapped[List["AgentRecommendation"]] = relationship(
        back_populates="conversation"
    )


class AgentAction(Base):
    __tablename__ = "AgentAction"

    ActionID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ConversationID: Mapped[Optional[int]] = mapped_column(
        ForeignKey("AgentConversation.ConversationID")
    )
    ActionType: Mapped[str] = mapped_column(String(50), nullable=False)
    TargetEntity: Mapped[Optional[str]] = mapped_column(String(50))
    TargetId: Mapped[Optional[int]] = mapped_column(Integer)
    ProposedPayloadJson: Mapped[str] = mapped_column(Text, nullable=False)
    Rationale: Mapped[Optional[str]] = mapped_column(Text)
    ConfidenceScore: Mapped[float] = mapped_column(Float, default=0.75)
    Status: Mapped[str] = mapped_column(String(20), default="pending")
    ProposedBy: Mapped[Optional[str]] = mapped_column(String(100))
    ProposedAt: Mapped[str] = mapped_column(String(30), server_default=func.now())
    ReviewedBy: Mapped[Optional[str]] = mapped_column(String(100))
    ReviewedAt: Mapped[Optional[str]] = mapped_column(String(30))
    ExecutionResult: Mapped[Optional[str]] = mapped_column(Text)

    conversation: Mapped[Optional["AgentConversation"]] = relationship(
        back_populates="actions"
    )


class AgentRecommendation(Base):
    __tablename__ = "AgentRecommendation"

    RecommendationID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ConversationID: Mapped[Optional[int]] = mapped_column(
        ForeignKey("AgentConversation.ConversationID")
    )
    RecommendationType: Mapped[str] = mapped_column(String(50), nullable=False)
    Title: Mapped[str] = mapped_column(Text, nullable=False)
    Description: Mapped[Optional[str]] = mapped_column(Text)
    Priority: Mapped[int] = mapped_column(Integer, default=5)
    EstimatedImpactJson: Mapped[Optional[str]] = mapped_column(Text)
    RelatedActionIDs: Mapped[Optional[str]] = mapped_column(Text)
    Status: Mapped[str] = mapped_column(String(20), default="proposed")
    CreatedAt: Mapped[str] = mapped_column(String(30), server_default=func.now())

    conversation: Mapped[Optional["AgentConversation"]] = relationship(
        back_populates="recommendations"
    )


class AgentAuditLog(Base):
    __tablename__ = "AgentAuditLog"

    LogID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    Timestamp: Mapped[str] = mapped_column(String(30), server_default=func.now(), index=True)
    AgentName: Mapped[Optional[str]] = mapped_column(String(100))
    ConversationID: Mapped[Optional[int]] = mapped_column(
        ForeignKey("AgentConversation.ConversationID")
    )
    ActionID: Mapped[Optional[int]] = mapped_column(ForeignKey("AgentAction.ActionID"))
    EventType: Mapped[str] = mapped_column(String(50), nullable=False)
    DetailsJson: Mapped[Optional[str]] = mapped_column(Text)


# =============================================================================
# Missing supporting models for MRP / Purchasing execution (critical for Agent approvals)
# =============================================================================


class ReturnReason(Base):
    __tablename__ = "ReturnReason"

    ReturnReasonID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ReasonCode: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    ReasonDescription: Mapped[str] = mapped_column(String(255), nullable=False)
    IsActive: Mapped[bool] = mapped_column(Boolean, default=True)


class Supplier(Base):
    __tablename__ = "Supplier"

    SupplierID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    SupplierCode: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    SupplierName: Mapped[str] = mapped_column(String(255), nullable=False)
    ContactName: Mapped[Optional[str]] = mapped_column(String(100))
    Email: Mapped[Optional[str]] = mapped_column(String(100))
    Phone: Mapped[Optional[str]] = mapped_column(String(20))
    Address: Mapped[Optional[str]] = mapped_column(String(255))
    City: Mapped[Optional[str]] = mapped_column(String(100))
    State: Mapped[Optional[str]] = mapped_column(String(50))
    ZipCode: Mapped[Optional[str]] = mapped_column(String(20))
    Country: Mapped[Optional[str]] = mapped_column(String(50))
    PaymentTerms: Mapped[Optional[str]] = mapped_column(String(100))
    Rating: Mapped[Optional[float]] = mapped_column(Float)
    IsActive: Mapped[bool] = mapped_column(Boolean, default=True)
    CreatedDate: Mapped[str] = mapped_column(String(30), server_default=func.now())

    # Relationships added for agent tools
    supplier_items: Mapped[List["SupplierItem"]] = relationship(
        back_populates="supplier", cascade="all, delete-orphan"
    )


class SupplierItem(Base):
    __tablename__ = "SupplierItem"

    SupplierItemID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    SupplierID: Mapped[int] = mapped_column(ForeignKey("Supplier.SupplierID"), nullable=False, index=True)
    ItemID: Mapped[int] = mapped_column(ForeignKey("Items.ItemID"), nullable=False, index=True)
    SupplierPartNumber: Mapped[Optional[str]] = mapped_column(String(100))
    UnitPrice: Mapped[float] = mapped_column(Float, nullable=False)
    MinimumOrderQuantity: Mapped[float] = mapped_column(Float, default=1.0)
    LeadTimeDays: Mapped[int] = mapped_column(Integer, default=0)
    IsPreferred: Mapped[bool] = mapped_column(Boolean, default=False)
    EffectiveDate: Mapped[Optional[str]] = mapped_column(String(30))
    EndDate: Mapped[Optional[str]] = mapped_column(String(30))

    supplier: Mapped["Supplier"] = relationship(back_populates="supplier_items")
    item: Mapped["Item"] = relationship()


class PurchaseOrder(Base):
    __tablename__ = "PurchaseOrder"

    PurchaseOrderID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    PONumber: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    SupplierID: Mapped[int] = mapped_column(ForeignKey("Supplier.SupplierID"), nullable=False)
    WarehouseID: Mapped[int] = mapped_column(ForeignKey("Warehouse.WarehouseID"), nullable=False)
    OrderDate: Mapped[str] = mapped_column(String(30), server_default=func.now())
    ExpectedDeliveryDate: Mapped[Optional[str]] = mapped_column(String(30))
    ActualDeliveryDate: Mapped[Optional[str]] = mapped_column(String(30))
    Status: Mapped[str] = mapped_column(String(20), default="Draft", index=True)
    Subtotal: Mapped[float] = mapped_column(Float, default=0.0)
    TaxAmount: Mapped[float] = mapped_column(Float, default=0.0)
    ShippingAmount: Mapped[float] = mapped_column(Float, default=0.0)
    TotalAmount: Mapped[float] = mapped_column(Float, default=0.0)
    Notes: Mapped[Optional[str]] = mapped_column(Text)
    CreatedBy: Mapped[Optional[str]] = mapped_column(String(100))
    CreatedDate: Mapped[str] = mapped_column(String(30), server_default=func.now())
    ModifiedDate: Mapped[str] = mapped_column(String(30), server_default=func.now())

    supplier: Mapped["Supplier"] = relationship()
    warehouse: Mapped["Warehouse"] = relationship()

    details: Mapped[List["PurchaseOrderDetail"]] = relationship(
        back_populates="purchase_order", cascade="all, delete-orphan"
    )


class PurchaseOrderDetail(Base):
    __tablename__ = "PurchaseOrderDetail"

    PODetailID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    PurchaseOrderID: Mapped[int] = mapped_column(
        ForeignKey("PurchaseOrder.PurchaseOrderID"), nullable=False, index=True
    )
    LineNumber: Mapped[int] = mapped_column(Integer, nullable=False)
    ItemID: Mapped[int] = mapped_column(ForeignKey("Items.ItemID"), nullable=False)
    Quantity: Mapped[float] = mapped_column(Float, nullable=False)
    UnitPrice: Mapped[float] = mapped_column(Float, nullable=False)
    QuantityReceived: Mapped[float] = mapped_column(Float, default=0.0)

    purchase_order: Mapped["PurchaseOrder"] = relationship(back_populates="details")
    item: Mapped["Item"] = relationship()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "Base",
    "UnitOfMeasure",
    "ItemType",
    "TransactionType",
    "SalesChannel",
    "ReturnReason",
    "Item",
    "BillOfMaterials",
    "Warehouse",
    "Inventory",
    "InventoryTransaction",
    "WorkCenter",
    "ProductionOrder",
    "ProductionOrderMaterial",
    "ProductionCompletion",
    "QualityInspection",
    "Customer",
    "SalesOrder",
    "SalesOrderDetail",
    "Supplier",
    "SupplierItem",
    "PurchaseOrder",
    "PurchaseOrderDetail",
    "AgentConversation",
    "AgentAction",
    "AgentRecommendation",
    "AgentAuditLog",
]
