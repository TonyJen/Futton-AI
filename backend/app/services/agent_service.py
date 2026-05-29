"""
Agent Service - handles proposal listing and basic agent metadata.
"""

from __future__ import annotations

from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AgentAction


class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_pending_proposals(self, status: str = "proposed") -> List[Dict[str, Any]]:
        stmt = select(AgentAction).where(AgentAction.Status == status)
        actions = (await self.db.execute(stmt)).scalars().all()

        return [
            {
                "action_id": a.ActionID,
                "action_type": a.ActionType,
                "payload": __import__("json").loads(a.ProposedPayloadJson),
                "rationale": a.Rationale,
                "confidence": a.ConfidenceScore,
                "status": a.Status,
                "proposed_by": a.ProposedBy,
            }
            for a in actions
        ]


async def get_agent_service(db: AsyncSession) -> AgentService:
    return AgentService(db)
