"""
Approval workflow for agent proposals.

This module enforces the "propose only" rule:
- Agents call propose_action() → creates records with status="proposed"
- Humans later call approve / reject via the API
- Only after approval does real business logic execute (in action_executor)
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AgentAction, AgentRecommendation, AgentAuditLog


async def propose_action(
    db: AsyncSession,
    *,
    agent_name: str,
    conversation_id: int,
    action_type: str,
    payload: Dict[str, Any],
    rationale: str,
    confidence: float = 0.75,
) -> int:
    """
    Called by agents when they want to suggest a change.
    Creates an AgentAction with status="proposed".
    Returns the ActionID.
    """
    action = AgentAction(
        ConversationID=conversation_id,
        ActionType=action_type,
        ProposedPayloadJson=json.dumps(payload),
        Rationale=rationale,
        ConfidenceScore=confidence,
        Status="proposed",
        ProposedBy=agent_name,
    )
    db.add(action)
    await db.flush()

    # Also log it
    log = AgentAuditLog(
        AgentName=agent_name,
        ConversationID=conversation_id,
        ActionID=action.ActionID,
        EventType="proposal_created",
        DetailsJson=json.dumps({"action_type": action_type}),
    )
    db.add(log)
    await db.flush()

    return action.ActionID


class ApprovalWorkflow:
    """High level facade used by the API router."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_pending_proposals(self) -> list[Dict[str, Any]]:
        # Simplified query - in real system join with recommendations etc.
        from sqlalchemy import select
        stmt = select(AgentAction).where(AgentAction.Status == "proposed")
        actions = (await self.db.execute(stmt)).scalars().all()

        return [
            {
                "action_id": a.ActionID,
                "action_type": a.ActionType,
                "payload": json.loads(a.ProposedPayloadJson),
                "rationale": a.Rationale,
                "confidence": a.ConfidenceScore,
                "proposed_by": a.ProposedBy,
            }
            for a in actions
        ]
