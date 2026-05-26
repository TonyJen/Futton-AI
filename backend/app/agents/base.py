"""
BaseAgent — common foundation for all specialist agents.

Provides:
- DB session
- Access to the powerful tool factory
- Convenience for proposing actions (via approval)
- Audit helpers
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.tools import get_manufacturing_tools
from app.agents.approval import propose_action
from app.db.models import AgentConversation


class BaseAgent:
    """All agents inherit from this. Enforces propose-only discipline."""

    name: str = "base_agent"

    def __init__(self, db: AsyncSession):
        self.db = db
        self.tools = get_manufacturing_tools(db)  # list of @tool decorated callables

    async def _ensure_conversation(self, user_id: Optional[str] = None) -> int:
        conv = AgentConversation(
            AgentName=self.name,
            UserId=user_id,
            Title=f"{self.name} analysis",
            Status="active",
        )
        self.db.add(conv)
        await self.db.flush()
        return conv.ConversationID

    async def propose(
        self,
        conversation_id: int,
        action_type: str,
        payload: Dict[str, Any],
        rationale: str,
        confidence: float = 0.75,
    ) -> int:
        """Convenience wrapper — the ONLY way an agent suggests change."""
        return await propose_action(
            self.db,
            agent_name=self.name,
            conversation_id=conversation_id,
            action_type=action_type,
            payload=payload,
            rationale=rationale,
            confidence=confidence,
        )

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override in subclass. Must return proposals_created count etc."""
        raise NotImplementedError
