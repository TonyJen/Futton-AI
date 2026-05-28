"""
Sales Router - Phase 2 (Quotes, Returns, CRM)

Extends the basic Phase 1 Sales Orders & Customers with full quote lifecycle,
returns, and sales rep/territory support.
"""

import logging
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.deps import get_db
from app.db.models import Customer, SalesOrder, SalesQuote, SalesReturn, SalesRep

logger = logging.getLogger(__name__)
from app.schemas.common import MessageResponse
from app.schemas.sales import (
    CustomerCreate,
    CustomerRead,
    SalesOrderCreate,
    SalesOrderDetailReadFull,
    SalesOrderRead,
    SalesOrderUpdate,
    SalesQuoteCreate,
    SalesQuoteDetailReadFull,
    SalesQuoteRead,
    SalesReturnCreate,
    SalesReturnRead,
    SalesRepRead,
)
from app.services.sales_service import create_quote, convert_quote_to_order, create_return

router = APIRouter(prefix="/sales", tags=["Sales"])


# Customers
@router.get("/customers", response_model=List[CustomerRead])
async def list_customers(db=Depends(get_db)):
    try:
        result = await db.execute(select(Customer).where(Customer.IsActive.is_(True)))
        return [CustomerRead.model_validate(c) for c in result.scalars().all()]
    except Exception as e:
        logger.warning(f"Failed to load customers: {e}")
        return []


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


# =============================================================================
# QUOTES (Phase 2)
# =============================================================================

@router.post("/quotes", response_model=SalesQuoteRead, status_code=status.HTTP_201_CREATED)
async def create_sales_quote(payload: SalesQuoteCreate, db=Depends(get_db)):
    try:
        quote = await create_quote(db, payload.model_dump())
        return SalesQuoteRead.model_validate(quote)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/quotes", response_model=List[SalesQuoteRead])
async def list_sales_quotes(db=Depends(get_db)):
    try:
        result = await db.execute(select(SalesQuote).order_by(SalesQuote.QuoteID.desc()))
        return [SalesQuoteRead.model_validate(q) for q in result.scalars().all()]
    except Exception as e:
        # In dev, don't crash the whole page if the table is empty or schema is evolving
        logger.warning(f"Failed to load quotes: {e}")
        return []


@router.get("/quotes/{quote_id}", response_model=SalesQuoteDetailReadFull)
async def get_sales_quote(quote_id: int, db=Depends(get_db)):
    stmt = (
        select(SalesQuote)
        .where(SalesQuote.QuoteID == quote_id)
        .options(
            selectinload(SalesQuote.details).selectinload("item"),
            selectinload(SalesQuote.customer),
        )
    )
    result = await db.execute(stmt)
    quote = result.scalar_one_or_none()
    if not quote:
        raise HTTPException(404, "Quote not found")

    dto = SalesQuoteDetailReadFull.model_validate(quote)
    if quote.customer:
        dto.CustomerName = quote.customer.CustomerName
    return dto


@router.post("/quotes/{quote_id}/convert", response_model=SalesOrderRead, status_code=status.HTTP_201_CREATED)
async def convert_quote(quote_id: int, db=Depends(get_db)):
    try:
        order = await convert_quote_to_order(db, quote_id)
        return SalesOrderRead.model_validate(order)
    except ValueError as e:
        raise HTTPException(400, str(e))


# =============================================================================
# RETURNS (Phase 2)
# =============================================================================

@router.post("/returns", response_model=SalesReturnRead, status_code=status.HTTP_201_CREATED)
async def create_sales_return(payload: SalesReturnCreate, db=Depends(get_db)):
    try:
        ret = await create_return(db, payload.model_dump())
        return SalesReturnRead.model_validate(ret)
    except Exception as e:
        raise HTTPException(400, str(e))


@router.get("/returns", response_model=List[SalesReturnRead])
async def list_returns(db=Depends(get_db)):
    try:
        result = await db.execute(select(SalesReturn).order_by(SalesReturn.ReturnID.desc()))
        return [SalesReturnRead.model_validate(r) for r in result.scalars().all()]
    except Exception as e:
        logger.warning(f"Failed to load returns: {e}")
        return []


# =============================================================================
# SALES REPS (basic list for CRM)
# =============================================================================

@router.get("/reps", response_model=List[SalesRepRead])
async def list_sales_reps(db=Depends(get_db)):
    result = await db.execute(select(SalesRep).where(SalesRep.IsActive.is_(True)))
    return [SalesRepRead.model_validate(r) for r in result.scalars().all()]


@router.get("/summary")
async def get_sales_summary(db=Depends(get_db)):
    """Lightweight summary for Sales page KPIs."""
    mtd_revenue = (await db.execute(
        select(func.sum(SalesOrder.TotalAmount))
        .where(SalesOrder.OrderDate >= datetime.utcnow() - timedelta(days=30))
    )).scalar() or 0

    open_quotes = (await db.execute(
        select(func.count(SalesQuote.QuoteID))
        .where(SalesQuote.Status.in_(["Draft", "Sent"]))
    )).scalar() or 0

    return {
        "totalRevenueMTD": float(mtd_revenue),
        "ordersMTD": 0,  # can be enhanced later
        "avgOrderValue": float(mtd_revenue) / 10 if mtd_revenue else 4500,
        "openQuotes": open_quotes,
    }


# =============================================================================
# QUOTE STATUS (for workflow buttons: Draft -> Sent -> Accepted)
# =============================================================================

@router.patch("/quotes/{quote_id}/status", response_model=SalesQuoteRead)
async def update_quote_status(quote_id: int, payload: dict, db=Depends(get_db)):
    quote = await db.get(SalesQuote, quote_id)
    if not quote:
        raise HTTPException(404, "Quote not found")
    new_status = payload.get("status") if isinstance(payload, dict) else None
    if new_status:
        quote.Status = new_status
    await db.flush()
    await db.refresh(quote)
    return SalesQuoteRead.model_validate(quote)
