"""
Bill of Materials Router.
Primary Phase 1 feature: working recursive BOM explosion endpoint.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.deps import get_db
from app.schemas.bom import BOMCreate, BOMExplosionResult, BOMRead, BOMUpdate
from app.services.bom_service import BOMService

router = APIRouter(prefix="/bom", tags=["Bill of Materials"])


@router.get("/explosion/{item_id}", response_model=BOMExplosionResult)
async def explode_bom(
    item_id: int,
    quantity: float = Query(1.0, gt=0, description="Multiplier for top-level quantity"),
    db=Depends(get_db),
):
    """
    **The key Phase 1 endpoint.**

    Recursively explodes the multi-level BOM for the given finished good or component.

    - Accounts for scrap rates at every level
    - Returns a flat list suitable for MRP, costing, and production planning
    - Safe recursion with depth guard
    """
    service = BOMService(db)
    try:
        return await service.explode_bom(parent_item_id=item_id, parent_quantity=quantity)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/", response_model=List[BOMRead])
async def list_bom_entries(
    parent_item_id: Optional[int] = None,
    component_item_id: Optional[int] = None,
    db=Depends(get_db),
):
    service = BOMService(db)
    if parent_item_id:
        children = await service.get_bom_children(parent_item_id)
        return [BOMRead.model_validate(b) for b in children]
    return []


@router.post("/", response_model=BOMRead)
async def create_bom_entry(payload: BOMCreate, db=Depends(get_db)):
    from app.db.models import BillOfMaterial
    bom = BillOfMaterial(**payload.model_dump())
    db.add(bom)
    await db.flush()
    await db.refresh(bom)
    return BOMRead.model_validate(bom)


@router.patch("/{bom_id}", response_model=BOMRead)
async def update_bom_entry(bom_id: int, payload: BOMUpdate, db=Depends(get_db)):
    from app.db.models import BillOfMaterial
    bom = await db.get(BillOfMaterial, bom_id)
    if not bom:
        raise HTTPException(status_code=404, detail="BOM entry not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(bom, field, value)

    await db.flush()
    await db.refresh(bom)
    return BOMRead.model_validate(bom)
