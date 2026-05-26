"""
Pydantic schemas for the AI Agents API.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    agent_name: str
    params: Dict[str, Any] = Field(default_factory=dict)


class AgentRunResponse(BaseModel):
    run_id: str
    agent_name: str
    status: str
    proposals_created: int = 0
    conversation_id: Optional[int] = None
    reasoning_trace: List[str] = Field(default_factory=list)


class ProposalItem(BaseModel):
    action_id: int
    action_type: str
    payload: Dict[str, Any]
    rationale: Optional[str] = None
    confidence: float = 0.75
    status: str = "proposed"
    proposed_by: Optional[str] = None


class ProposalListResponse(BaseModel):
    items: List[ProposalItem]
    total: int
    high_priority_count: int = 0


class ApprovalRequest(BaseModel):
    approved_by: str
    notes: Optional[str] = None


class ApprovalResponse(BaseModel):
    success: bool
    action_ids_executed: List[int] = Field(default_factory=list)
    message: str
    execution_details: Optional[Dict[str, Any]] = None


class RejectionRequest(BaseModel):
    rejected_by: str
    reason: str
