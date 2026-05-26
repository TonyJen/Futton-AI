"""
Sales Orders and Customers Router (Phase 1 basic CRUD).
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.deps import get_db
from app.db.models import Customer, SalesOrder
from app.schemas.common import MessageResponse
from app.schemas.sales import (
    CustomerCreate,
    CustomerRead,
    SalesOrderCreate,
    SalesOrderDetailReadFull,
    SalesOrderRead,
    SalesOrderUpdate,
)

router = APIRouter(prefix="/sales", tags=["Sales"])


# Customers
@router.get("/customers", response_model=List[CustomerRead])
async def list_customers(db=Depends(get_db)):
    result = await db.execute(select(Customer).where(Customer.IsActive.is_(True)))
    return [CustomerRead.model_validate(c) for c in result.scalars().all()]


@router.post("/customers", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(payload: CustomerCreate, db=Depends(get_db)):
    cust = Customer(**payload.model_dump())
    db.add(cust)
    await db.flush()
    await db.refresh(cust)
    return CustomerRead.model_validate(cust)


# Sales Orders
@router.get("/orders", response_model=List[SalesOrderRead])
async def list_sales_orders(db=Depends(get_db)):
    result = await db.execute(select(SalesOrder).order_by(SalesOrder.SalesOrderID.desc()))
    return [SalesOrderRead.model_validate(o) for o in result.scalars().all()]


@router.get("/orders/{order_id}", response_model=SalesOrderDetailReadFull)
async def get_sales_order(order_id: int, db=Depends(get_db)):
    from sqlalchemy.orm import selectinload

    stmt = (
        select(SalesOrder)
        .where(SalesOrder.SalesOrderID == order_id)
        .options(
            selectinload(SalesOrder.customer),
            selectinload(SalesOrder.warehouse),
            selectinload(SalesOrder.details).selectinload("item"),
        )
    )
    result = await db.execute(stmt)
    so = result.scalar_one_or_none()
    if not so:
        raise HTTPException(404, "Sales order not found")

    dto = SalesOrderDetailReadFull.model_validate(so)
    if so.customer:
        dto.CustomerName = so.customer.CustomerName
    if so.warehouse:
        dto.WarehouseName = so.warehouse.WarehouseName
    return dto


@router.post("/orders", response_model=SalesOrderRead, status_code=status.HTTP_201_CREATED)
async def create_sales_order(payload: SalesOrderCreate, db=Depends(get_db)):
    order_data = payload.model_dump(exclude={"details"})
    so = SalesOrder(**order_data)
    db.add(so)
    await db.flush()

    subtotal = 0.0
    from app.db.models import SalesOrderDetail

    for detail in payload.details:
        line = SalesOrderDetail(SalesOrderID=so.SalesOrderID, **detail.model_dump())
        db.add(line)
        subtotal += detail.Quantity * detail.UnitPrice

    so.Subtotal = subtotal
    so.TotalAmount = subtotal + so.TaxAmount + so.ShippingAmount - so.DiscountAmount

    await db.flush()
    await db.refresh(so)
    return SalesOrderRead.model_validate(so)


@router.patch("/orders/{order_id}", response_model=SalesOrderRead)
async def update_sales_order(order_id: int, payload: SalesOrderUpdate, db=Depends(get_db)):
    so = await db.get(SalesOrder, order_id)
    if not so:
        raise HTTPException(404, "Sales order not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(so, field, value)

    await db.flush()
    await db.refresh(so)
    return SalesOrderRead.model_validate(so)
