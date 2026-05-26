"""
Items & BOM Router (Phase 1)

Endpoints:
- GET /items (with filters)
- GET /items/{item_id}/bom (full recursive explosion)
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.core.dependencies import DBSessionDep
from app.schemas.item import (
    BOMExplosionResponse,
    Item,
    ItemFilter,
)
from app.services.bom_service import get_full_bom_explosion

from app.db.models import Item as ItemModel
from sqlalchemy import select

router = APIRouter(prefix="/items", tags=["Items & BOM"])


@router.get("", response_model=List[Item])
async def list_items(
    db: DBSessionDep,
    item_type: Optional[str] = Query(None, description="Filter by type code: RAW | COMP | FG"),
    is_active: bool = Query(True),
    search: Optional[str] = Query(None, min_length=1, description="Search ItemCode or ItemName"),
    limit: int = Query(100, le=500),
) -> List[Item]:
    """List items with basic filters. Strong typing via Pydantic."""
    stmt = select(ItemModel).order_by(ItemModel.ItemCode)

    if item_type:
        from app.db.models import ItemType

        stmt = stmt.join(ItemModel.item_type).where(ItemType.TypeCode == item_type)
    if is_active is not None:
        stmt = stmt.where(ItemModel.IsActive == is_active)
    if search:
        stmt = stmt.where(
            (ItemModel.ItemCode.ilike(f"%{search}%")) | (ItemModel.ItemName.ilike(f"%{search}%"))
        )

    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    items = result.scalars().all()
    return [Item.model_validate(item) for item in items]


@router.get("/{item_id}/bom", response_model=BOMExplosionResponse)
async def get_item_bom(
    item_id: int,
    db: DBSessionDep,
    include_inactive: bool = Query(False),
) -> BOMExplosionResponse:
    """Full recursive BOM explosion for a finished good or component."""
    try:
        explosion = await get_full_bom_explosion(db, item_id, include_inactive=include_inactive)
        return explosion
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BOM explosion failed: {str(e)}")
