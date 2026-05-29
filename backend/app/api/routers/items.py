"""
Items & BOM Router (Phase 1)

Endpoints:
- GET /items (with filters)
- GET /items/{item_id}/bom (full recursive explosion)
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.dependencies import DBSessionDep
from app.db.models import Item as ItemModel
from app.schemas.bom import BOMExplosionResult
from app.services.bom_service import get_full_bom_explosion

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/items", tags=["Items & BOM"])


@router.get("", response_model=List[dict])
async def list_items(
    db: DBSessionDep,
    item_type: Optional[str] = Query(None, alias="type", description="Filter by type: Raw Material | Component | Finished Good | Packaging"),
    is_active: bool = Query(True),
    search: Optional[str] = Query(None, description="Search ItemCode or ItemName"),
    limit: int = Query(100, le=500),
) -> List[dict]:
    """List items shaped for the frontend (camelCase + resolved type name)."""
    from app.db.models import ItemType as ItemTypeModel

    stmt = (
        select(ItemModel)
        .outerjoin(ItemModel.item_type)
        .options(selectinload(ItemModel.item_type))
        .order_by(ItemModel.ItemCode)
    )

    if item_type and item_type != "All":
        stmt = stmt.where(ItemTypeModel.TypeCode == item_type)

    if is_active is not None:
        stmt = stmt.where(ItemModel.IsActive == is_active)
    if search:
        stmt = stmt.where(
            (ItemModel.ItemCode.ilike(f"%{search}%")) | (ItemModel.ItemName.ilike(f"%{search}%"))
        )

    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    rows = result.scalars().all()

    shaped = []
    for item in rows:
        try:
            itype = item.item_type
            shaped.append({
                "itemId": item.ItemID,
                "itemCode": item.ItemCode,
                "itemName": item.ItemName,
                "itemType": (itype.TypeCode if itype else "Unknown"),
                "unit": "",
                "description": item.Description,
                "standardCost": float(item.StandardCost or 0),
                "listPrice": float(item.ListPrice or 0),
                "isActive": item.IsActive,
                "leadTimeDays": item.LeadTimeDays or 0,
                "reorderPoint": float(item.ReorderPoint or 0),
                "safetyStock": float(item.SafetyStock or 0),
            })
        except Exception as item_err:
            # Skip bad rows instead of crashing the whole list
            logger.warning(f"Skipping item {getattr(item, 'ItemID', 'unknown')}: {item_err}")
    return shaped


@router.get("/{item_id}/bom", response_model=BOMExplosionResult)
async def get_item_bom(
    item_id: int,
    db: DBSessionDep,
    include_inactive: bool = Query(False),
) -> BOMExplosionResult:
    """Full recursive BOM explosion for a finished good or component."""
    try:
        explosion = await get_full_bom_explosion(db, item_id, include_inactive=include_inactive)
        return explosion
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BOM explosion failed: {str(e)}")
