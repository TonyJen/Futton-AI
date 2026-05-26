"""
Item master data service layer.
"""

from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Item
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate, ItemWithTypeRead


class ItemService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_items(
        self, skip: int = 0, limit: int = 50, search: Optional[str] = None, is_active: Optional[bool] = None
    ) -> List[ItemWithTypeRead]:
        stmt = (
            select(Item)
            .options(selectinload(Item.item_type), selectinload(Item.unit))
            .offset(skip)
            .limit(limit)
            .order_by(Item.ItemCode)
        )
        if search:
            stmt = stmt.where(
                or_(
                    Item.ItemCode.ilike(f"%{search}%"),
                    Item.ItemName.ilike(f"%{search}%"),
                )
            )
        if is_active is not None:
            stmt = stmt.where(Item.IsActive.is_(is_active))

        result = await self.db.execute(stmt)
        items = result.scalars().all()

        enriched = []
        for item in items:
            dto = ItemWithTypeRead.model_validate(item)
            if item.item_type:
                dto.ItemTypeName = item.item_type.TypeName
            if item.unit:
                dto.UnitCode = item.unit.UnitCode
                dto.UnitName = item.unit.UnitName
            enriched.append(dto)
        return enriched

    async def get_item(self, item_id: int) -> Optional[ItemWithTypeRead]:
        stmt = (
            select(Item)
            .where(Item.ItemID == item_id)
            .options(selectinload(Item.item_type), selectinload(Item.unit))
        )
        result = await self.db.execute(stmt)
        item = result.scalar_one_or_none()
        if not item:
            return None

        dto = ItemWithTypeRead.model_validate(item)
        if item.item_type:
            dto.ItemTypeName = item.item_type.TypeName
        if item.unit:
            dto.UnitCode = item.unit.UnitCode
            dto.UnitName = item.unit.UnitName
        return dto

    async def create_item(self, payload: ItemCreate) -> ItemRead:
        item = Item(**payload.model_dump())
        self.db.add(item)
        await self.db.flush()
        await self.db.refresh(item)
        return ItemRead.model_validate(item)

    async def update_item(self, item_id: int, payload: ItemUpdate) -> Optional[ItemRead]:
        item = await self.db.get(Item, item_id)
        if not item:
            return None

        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        await self.db.flush()
        await self.db.refresh(item)
        return ItemRead.model_validate(item)

    async def delete_item(self, item_id: int) -> bool:
        item = await self.db.get(Item, item_id)
        if not item:
            return False
        await self.db.delete(item)
        await self.db.flush()
        return True
