"""
Pydantic schemas for Production Orders and related entities.
"""

from typing import List, Optional

from pydantic import Field

from .common import BaseSchema, TimestampSchema


class ProductionOrderBase(BaseSchema):
    WorkOrderNumber: str = Field(..., max_length=50)
    ItemID: int
    WarehouseID: int
    WorkCenterID: Optional[int] = None
    OrderQuantity: float = Field(..., gt=0)
    StartDate: Optional[str] = None
    PlannedCompletionDate: Optional[str] = None
    Status: str = "Planned"
    Priority: int = 5
    Notes: Optional[str] = None
    CreatedBy: Optional[str] = None


class ProductionOrderCreate(ProductionOrderBase):
    pass


class ProductionOrderUpdate(BaseSchema):
    OrderQuantity: Optional[float] = Field(None, gt=0)
    QuantityCompleted: Optional[float] = None
    QuantityScrapped: Optional[float] = None
    StartDate: Optional[str] = None
    PlannedCompletionDate: Optional[str] = None
    ActualCompletionDate: Optional[str] = None
    Status: Optional[str] = None
    Priority: Optional[int] = None
    Notes: Optional[str] = None
    WorkCenterID: Optional[int] = None


class ProductionOrderRead(ProductionOrderBase, TimestampSchema):
    ProductionOrderID: int
    QuantityCompleted: float = 0.0
    QuantityScrapped: float = 0.0
    ActualCompletionDate: Optional[str] = None


class ProductionOrderWithDetailsRead(ProductionOrderRead):
    ItemCode: Optional[str] = None
    ItemName: Optional[str] = None
    WarehouseName: Optional[str] = None
    WorkCenterName: Optional[str] = None


class ProductionOrderMaterialRead(BaseSchema):
    ProdOrderMaterialID: int
    ItemID: int
    RequiredQuantity: float
    IssuedQuantity: float = 0.0
    ItemCode: Optional[str] = None
    ItemName: Optional[str] = None


class ProductionOrderDetailRead(ProductionOrderWithDetailsRead):
    """Includes exploded materials for the work order."""
    Materials: List[ProductionOrderMaterialRead] = []


class ProductionCompletionRequest(BaseSchema):
    """Request to record completion against a production order."""
    QuantityCompleted: float = Field(..., gt=0)
    QuantityScrapped: float = 0.0
    WorkCenterID: Optional[int] = None
    Notes: Optional[str] = None
    CompletedBy: str = "api_user"
