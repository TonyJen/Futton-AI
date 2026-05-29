"""
Sales Service Layer (Phase 2)

Handles business logic for:
- Sales Quotes (creation, conversion)
- Sales Returns
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import (
    Item,
    SalesOrder,
    SalesOrderDetail,
    SalesQuote,
    SalesQuoteDetail,
    SalesReturn,
    SalesReturnDetail,
)

# =============================================================================
# QUOTE SERVICES
# =============================================================================

async def get_next_sales_order_number(db: AsyncSession) -> str:
    year = datetime.now().year
    latest_order_number = (
        await db.execute(
            select(func.max(SalesOrder.OrderNumber)).where(
                SalesOrder.OrderNumber.like(f"SO-{year}-%")
            )
        )
    ).scalar_one_or_none()
    next_sequence = int(latest_order_number.rsplit("-", 1)[-1]) + 1 if latest_order_number else 1
    return f"SO-{year}-{next_sequence:04d}"


async def create_quote(db: AsyncSession, payload: dict) -> SalesQuote:
    """Create a new Sales Quote with details."""
    quote_data = {k: v for k, v in payload.items() if k != "details"}

    # Generate Quote Number
    year = datetime.now().year
    count_stmt = select(SalesQuote).where(SalesQuote.QuoteDate.like(f"{year}-%"))
    count = len((await db.execute(count_stmt)).scalars().all()) + 1
    quote_number = f"QT-{year}-{count:04d}"

    quote = SalesQuote(
        QuoteNumber=quote_number,
        QuoteDate=datetime.now().strftime("%Y-%m-%d"),
        **quote_data,
    )
    db.add(quote)
    await db.flush()

    subtotal = 0.0
    for i, detail in enumerate(payload.get("details", []), 1):
        item = await db.get(Item, detail["ItemID"])
        if not item:
            raise ValueError(f"Item {detail['ItemID']} not found")

        unit_price = detail.get("UnitPrice", item.ListPrice or 0)
        discount = detail.get("DiscountPercent", 0)

        line = SalesQuoteDetail(
            QuoteID=quote.QuoteID,
            LineNumber=i,
            ItemID=detail["ItemID"],
            Quantity=detail["Quantity"],
            UnitPrice=unit_price,
            DiscountPercent=discount,
        )
        db.add(line)

        line_total = detail["Quantity"] * unit_price * (1 - discount / 100)
        subtotal += line_total

    quote.Subtotal = subtotal
    quote.TotalAmount = subtotal + quote.TaxAmount - quote.DiscountAmount

    await db.flush()
    await db.refresh(quote)
    return quote


async def get_quote_with_details(db: AsyncSession, quote_id: int) -> Optional[SalesQuote]:
    stmt = (
        select(SalesQuote)
        .where(SalesQuote.QuoteID == quote_id)
        .options(
            selectinload(SalesQuote.details).selectinload(SalesQuoteDetail.item),
            selectinload(SalesQuote.customer),
        )
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def convert_quote_to_order(db: AsyncSession, quote_id: int) -> SalesOrder:
    """Convert an accepted quote into a Sales Order."""
    quote = await get_quote_with_details(db, quote_id)
    if not quote:
        raise ValueError("Quote not found")

    if quote.Status != "Accepted":
        raise ValueError("Only accepted quotes can be converted to orders")

    # Create Sales Order

    order = SalesOrder(
        OrderNumber=await get_next_sales_order_number(db),
        CustomerID=quote.CustomerID,
        WarehouseID=1,  # Default warehouse - can be improved later
        SalesChannelID=quote.SalesChannelID,
        SalesRepID=quote.SalesRepID,
        OrderDate=datetime.now().strftime("%Y-%m-%d"),
        Status="Draft",
        Subtotal=quote.Subtotal,
        TaxAmount=quote.TaxAmount,
        ShippingAmount=0.0,
        DiscountAmount=quote.DiscountAmount,
        TotalAmount=quote.TotalAmount,
        Notes=f"Converted from Quote {quote.QuoteNumber}",
        CreatedBy="System (Quote Conversion)",
    )
    db.add(order)
    await db.flush()

    # Copy details
    for qd in quote.details:
        line = SalesOrderDetail(
            SalesOrderID=order.SalesOrderID,
            LineNumber=qd.LineNumber,
            ItemID=qd.ItemID,
            Quantity=qd.Quantity,
            UnitPrice=qd.UnitPrice,
            DiscountPercent=qd.DiscountPercent,
        )
        db.add(line)

    # Mark quote as converted
    quote.Status = "Accepted"
    quote.ConvertedToOrderID = order.SalesOrderID

    await db.flush()
    await db.refresh(order)
    return order


# =============================================================================
# RETURN SERVICES (basic for Phase 2 start)
# =============================================================================

async def create_return(db: AsyncSession, payload: dict) -> SalesReturn:
    """Create a Sales Return with details."""
    return_data = {k: v for k, v in payload.items() if k != "details"}

    # Generate Return Number
    year = datetime.now().year
    count_stmt = select(SalesReturn).where(SalesReturn.ReturnDate.like(f"{year}-%"))
    count = len((await db.execute(count_stmt)).scalars().all()) + 1
    return_number = f"RT-{year}-{count:04d}"

    ret = SalesReturn(
        ReturnNumber=return_number,
        ReturnDate=datetime.now().strftime("%Y-%m-%d"),
        **return_data,
    )
    db.add(ret)
    await db.flush()

    total_refund = 0.0
    for detail in payload.get("details", []):
        line = SalesReturnDetail(
            ReturnID=ret.ReturnID,
            SODetailID=detail.get("SODetailID"),
            ItemID=detail["ItemID"],
            QuantityReturned=detail["QuantityReturned"],
            UnitPrice=detail["UnitPrice"],
            RefundAmount=detail["RefundAmount"],
            Disposition=detail.get("Disposition"),
        )
        db.add(line)
        total_refund += detail["RefundAmount"]

    ret.RefundAmount = total_refund
    await db.flush()
    await db.refresh(ret)
    return ret
