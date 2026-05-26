"""
Production Order domain services.
Includes material requirements lookup using BOM service.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import ProductionOrder, ProductionOrderMaterial
from app.schemas.production import (
    ProductionCompletionRequest,
    ProductionOrderCreate,
    ProductionOrderDetailRead,
    ProductionOrderRead,
    ProductionOrderUpdate,
)
from app.services.bom_service import BOMService


class ProductionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.bom_service = BOMService(db)

    async def list_orders(self, status: Optional[str] = None) -> List[ProductionOrderRead]:
        stmt = select(ProductionOrder).order_by(ProductionOrder.ProductionOrderID.desc())
        if status:
            stmt = stmt.where(ProductionOrder.Status == status)

        result = await self.db.execute(stmt)
        return [ProductionOrderRead.model_validate(o) for o in result.scalars().all()]

    async def get_order_detail(self, order_id: int) -> Optional[ProductionOrderDetailRead]:
        stmt = (
            select(ProductionOrder)
            .where(ProductionOrder.ProductionOrderID == order_id)
            .options(
                selectinload(ProductionOrder.item),
                selectinload(ProductionOrder.warehouse),
                selectinload(ProductionOrder.work_center),
                selectinload(ProductionOrder.materials).selectinload(ProductionOrderMaterial.item),
            )
        )
        result = await self.db.execute(stmt)
        order = result.scalar_one_or_none()
        if not order:
            return None

        dto = ProductionOrderDetailRead.model_validate(order)

        if order.item:
            dto.ItemCode = order.item.ItemCode
            dto.ItemName = order.item.ItemName
        if order.warehouse:
            dto.WarehouseName = order.warehouse.WarehouseName
        if order.work_center:
            dto.WorkCenterName = order.work_center.WorkCenterName

        # Enrich materials
        materials = []
        for mat in order.materials:
            m = {
                "ProdOrderMaterialID": mat.ProdOrderMaterialID,
                "ItemID": mat.ItemID,
                "RequiredQuantity": mat.RequiredQuantity,
                "IssuedQuantity": mat.IssuedQuantity,
            }
            if mat.item:
                m["ItemCode"] = mat.item.ItemCode
                m["ItemName"] = mat.item.ItemName
            materials.append(m)

        dto.Materials = materials
        return dto

    async def create_order(self, payload: ProductionOrderCreate) -> ProductionOrderRead:
        order = ProductionOrder(**payload.model_dump())
        self.db.add(order)
        await self.db.flush()

        # Optionally auto-populate materials from current BOM explosion
        # (commented to keep simple; agents can call this explicitly)
        # await self._populate_materials_from_bom(order)

        await self.db.refresh(order)
        return ProductionOrderRead.model_validate(order)

    async def update_order(
        self, order_id: int, payload: ProductionOrderUpdate
    ) -> Optional[ProductionOrderRead]:
        order = await self.db.get(ProductionOrder, order_id)
        if not order:
            return None

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(order, field, value)

        await self.db.flush()
        await self.db.refresh(order)
        return ProductionOrderRead.model_validate(order)

    async def record_completion(
        self, order_id: int, completion: ProductionCompletionRequest
    ) -> Optional[ProductionOrderRead]:
        order = await self.db.get(ProductionOrder, order_id)
        if not order:
            return None

        order.QuantityCompleted += completion.QuantityCompleted
        order.QuantityScrapped += completion.QuantityScrapped

        if order.QuantityCompleted + order.QuantityScrapped >= order.OrderQuantity:
            order.Status = "Completed"
            order.ActualCompletionDate = completion.Notes or "auto"

        await self.db.flush()
        await self.db.refresh(order)
        return ProductionOrderRead.model_validate(order)

    # Helper example for agents
    async def suggest_materials_from_bom(self, item_id: int, order_qty: float) -> list:
        explosion = await self.bom_service.explode_bom(item_id, parent_quantity=order_qty)
        return [
            {
                "ItemID": c.ComponentItemID,
                "RequiredQuantity": c.TotalQuantityRequired,
                "ItemCode": c.ComponentItemCode,
            }
            for c in explosion.Components
        ]
