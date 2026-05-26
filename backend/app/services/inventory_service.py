"""
Inventory Intelligence Service — calculations for ABC, turnover, reorder suggestions.

Used by Inventory Agent tools and also available to reports/dashboard.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Inventory, InventoryTransaction, Item, ItemType


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_inventory_snapshot(
        self, item_ids: Optional[List[int]] = None, warehouse_id: Optional[int] = None
    ) -> Dict[int, Dict[str, Any]]:
        stmt = select(Inventory)
        if item_ids:
            stmt = stmt.where(Inventory.ItemID.in_(item_ids))
        if warehouse_id:
            stmt = stmt.where(Inventory.WarehouseID == warehouse_id)

        rows = (await self.db.execute(stmt)).scalars().all()
        snap = {}
        for inv in rows:
            key = inv.ItemID
            if key not in snap:
                snap[key] = {"on_hand": 0.0, "allocated": 0.0, "available": 0.0}
            snap[key]["on_hand"] += float(inv.QuantityOnHand or 0)
            snap[key]["allocated"] += float(inv.QuantityAllocated or 0)
            snap[key]["available"] += float((inv.QuantityOnHand or 0) - (inv.QuantityAllocated or 0))
        return snap

    async def compute_abc_analysis(
        self,
        warehouse_id: Optional[int] = None,
        a_threshold: float = 80.0,
        b_threshold: float = 95.0,
    ) -> List[Dict[str, Any]]:
        """ABC by current inventory value."""
        stmt = (
            select(
                Item.ItemID,
                Item.ItemCode,
                Item.ItemName,
                ItemType.TypeName.label("ItemType"),
                Inventory.QuantityOnHand,
                (Inventory.QuantityOnHand * Item.StandardCost).label("Value"),
            )
            .join(Inventory, Inventory.ItemID == Item.ItemID)
            .join(ItemType, Item.ItemTypeID == ItemType.ItemTypeID)
        )
        if warehouse_id:
            stmt = stmt.where(Inventory.WarehouseID == warehouse_id)

        rows = (await self.db.execute(stmt)).all()

        # Compute totals
        total_value = sum(float(r.Value or 0) for r in rows if r.Value)
        if total_value == 0:
            return []

        enriched = []
        for r in rows:
            val = float(r.Value or 0)
            pct = (val / total_value) * 100 if total_value else 0
            enriched.append({
                "ItemID": r.ItemID,
                "ItemCode": r.ItemCode,
                "ItemName": r.ItemName,
                "ItemType": r.ItemType,
                "QuantityOnHand": float(r.QuantityOnHand or 0),
                "InventoryValue": round(val, 2),
                "PercentOfTotal": round(pct, 2),
            })

        # Sort by value desc and compute cumulative
        enriched.sort(key=lambda x: x["InventoryValue"], reverse=True)
        cum = 0.0
        for row in enriched:
            cum += row["PercentOfTotal"]
            if cum <= a_threshold:
                row["ABCClass"] = "A"
            elif cum <= b_threshold:
                row["ABCClass"] = "B"
            else:
                row["ABCClass"] = "C"
            row["CumulativePercent"] = round(cum, 2)

        return enriched

    async def compute_turnover_analysis(self, lookback_days: int = 365) -> List[Dict[str, Any]]:
        """Simplified turnover + movement class (ported from reference vw_InventoryTurnover)."""
        cutoff = (datetime.utcnow() - timedelta(days=lookback_days)).isoformat()

        # Aggregate issues (negative qty) in period
        issue_stmt = (
            select(
                InventoryTransaction.ItemID,
                func.sum(func.abs(InventoryTransaction.Quantity)).label("Issued"),
            )
            .where(
                InventoryTransaction.Quantity < 0,
                InventoryTransaction.TransactionDate >= cutoff,
            )
            .group_by(InventoryTransaction.ItemID)
        )
        issues = {row[0]: float(row[1] or 0) for row in (await self.db.execute(issue_stmt)).all()}

        # Current inventory + item master
        inv_stmt = (
            select(Inventory, Item, ItemType)
            .join(Item, Inventory.ItemID == Item.ItemID)
            .join(ItemType, Item.ItemTypeID == ItemType.ItemTypeID)
        )
        rows = (await self.db.execute(inv_stmt)).all()

        out = []
        for inv, item, itype in rows:
            on_hand = float(inv.QuantityOnHand or 0)
            issued = issues.get(item.ItemID, 0.0)
            turns = issued / on_hand if on_hand > 0 else 0.0
            doh = (on_hand * 365.0) / issued if issued > 0 else 9999

            if turns >= 12:
                cls = "Fast Moving"
            elif turns >= 4:
                cls = "Normal"
            elif turns >= 1:
                cls = "Slow Moving"
            else:
                cls = "Non-Moving"

            out.append({
                "ItemID": item.ItemID,
                "ItemCode": item.ItemCode,
                "ItemName": item.ItemName,
                "ItemType": itype.TypeName,
                "QuantityOnHand": on_hand,
                "AnnualUsage": round(issued, 2),
                "TurnoverRatio": round(turns, 2),
                "DaysOnHand": round(doh, 1),
                "MovementClass": cls,
                "InventoryValue": round(on_hand * float(item.StandardCost or 0), 2),
            })

        return out

    async def generate_reorder_suggestions(
        self, item_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """Simple dynamic reorder model (lead time * avg daily usage + safety)."""
        stmt = select(Item, Inventory).join(Inventory, Inventory.ItemID == Item.ItemID)
        if item_ids:
            stmt = stmt.where(Item.ItemID.in_(item_ids))

        rows = (await self.db.execute(stmt)).all()
        suggestions = []

        for item, inv in rows:
            on_hand = float(inv.QuantityOnHand or 0)
            lead = item.LeadTimeDays or 14
            # Very naive daily usage estimate (real would use transaction history)
            est_daily = max(1.0, (item.ReorderPoint or 50) / 30.0)
            suggested_rp = round(est_daily * lead * 1.25 + (item.SafetyStock or 0) * 0.8, 0)

            if suggested_rp > (item.ReorderPoint or 0) * 1.1 or on_hand < suggested_rp * 0.6:
                suggestions.append({
                    "ItemID": item.ItemID,
                    "ItemCode": item.ItemCode,
                    "CurrentReorderPoint": float(item.ReorderPoint or 0),
                    "SuggestedReorderPoint": suggested_rp,
                    "SuggestedSafetyStock": round(suggested_rp * 0.25, 0),
                    "CurrentOnHand": on_hand,
                    "Rationale": f"Lead time {lead}d + usage estimate suggests raising reorder point.",
                })

        return suggestions
