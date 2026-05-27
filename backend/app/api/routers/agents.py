"""
/api/agents - Clean FastAPI surface for LangGraph agents + Human-in-the-Loop.

This router allows:
- Triggering the two MVP agents (MRP + Inventory)
- Listing the proposal queue
- Approving or rejecting proposals (the moment real data changes)

All agent logic lives under app/agents/. All mutations go through approved execution paths.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict, List, Optional

from app.core.dependencies import DBSessionDep
from app.db.models import AgentAction
from sqlalchemy.ext.asyncio import AsyncSession  # keep for type references if needed
from app.schemas.agent import (
    AgentRunRequest,
    AgentRunResponse,
    ApprovalRequest,
    ApprovalResponse,
    RejectionRequest,
    ProposalListResponse,
)
from app.services.agent_service import get_agent_service
from app.services.action_executor import get_executor

# Try to import approval workflow (may not exist yet)
try:
    from app.agents.approval import ApprovalWorkflow
except ImportError:
    ApprovalWorkflow = None

# Import the two concrete agents (LangGraph)
from app.agents.mrp_agent import MRPPlanningAgent
from app.agents.inventory_agent import InventoryIntelligenceAgent
from app.agents.production_scheduler_agent import ProductionSchedulerAgent

router = APIRouter(prefix="/agents", tags=["AI Agents (Phase 1)"])


@router.get("/available")
async def available_agents() -> Dict[str, Any]:
    """Agent catalog for frontend cards."""
    return {
        "mrp": {
            "name": "MRP & Material Planning Agent",
            "description": "Full BOM explosion, shortage detection against open orders, proposes purchase orders and production orders.",
            "status": "production",
        },
        "inventory": {
            "name": "Inventory Intelligence Agent",
            "description": "ABC analysis, slow mover detection, dynamic reorder suggestions.",
            "status": "production",
        },
        "production_scheduler": {
            "name": "Production Scheduler Agent",
            "description": "Capacity-aware scheduling, bottleneck detection, proposes release of production orders on available work centers.",
            "status": "production",
        },
    }


@router.post("/run", response_model=AgentRunResponse)
async def run_agent(
    req: AgentRunRequest,
    db: DBSessionDep,
) -> AgentRunResponse:
    """Trigger an agent run. Returns immediately after proposals are created (status=proposed)."""
    try:
        if req.agent_name == "mrp":
            agent = MRPPlanningAgent(db)
            result = await agent.run(req.params)
        elif req.agent_name == "inventory":
            agent = InventoryIntelligenceAgent(db)
            result = await agent.run(req.params)
        elif req.agent_name in ("production_scheduler", "scheduler"):
            agent = ProductionSchedulerAgent(db)
            result = await agent.run(req.params)
        else:
            raise HTTPException(400, f"Unknown agent: {req.agent_name}")

        return AgentRunResponse(
            run_id=result.get("run_id", "unknown"),
            agent_name=req.agent_name,
            status="completed",
            proposals_created=result.get("proposals_created", 0),
            conversation_id=result.get("conversation_id"),
            reasoning_trace=result.get("reasoning_trace", []),
        )
    except Exception as e:
        raise HTTPException(500, f"Agent execution error: {str(e)}")


@router.get("/proposals", response_model=ProposalListResponse)
async def get_proposals(
    db: DBSessionDep,
    status_filter: str = Query("proposed", alias="status"),
):
    """The approval queue shown in the AI Agents Hub."""
    svc = await get_agent_service(db)
    items = await svc.get_pending_proposals()
    return ProposalListResponse(
        items=items,
        total=len(items),
        high_priority_count=sum(1 for x in items if x.get("priority", 5) >= 8),
    )


@router.post("/actions/{action_id}/approve", response_model=ApprovalResponse)
async def approve_action_endpoint(
    action_id: int,
    body: ApprovalRequest,
    db: DBSessionDep,
):
    """Human approves → real business change happens here."""
    workflow = ApprovalWorkflow(db) if ApprovalWorkflow else None
    try:
        # Load action
        action = await db.get(AgentAction, action_id)
        if not action or action.Status != "proposed":
            raise HTTPException(400, "Action not in proposed state")

        import json
        executor = await get_executor(db)
        payload = json.loads(action.ProposedPayloadJson) if isinstance(action.ProposedPayloadJson, str) else action.ProposedPayloadJson
        exec_result = await executor.execute_proposal(
            {
                "action_type": action.ActionType,
                "payload": payload,
            },
            approved_by=body.approved_by,
        )

        # Update action record
        action.Status = "executed"
        action.ReviewedBy = body.approved_by
        action.ReviewedAt = __import__("datetime").datetime.utcnow().isoformat()
        action.ExecutionResult = str(exec_result)
        await db.commit()

        return ApprovalResponse(
            success=True,
            action_ids_executed=[action_id],
            message="Action approved and executed successfully",
            execution_details=exec_result,
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(500, f"Approve & execute failed: {e}")


@router.post("/actions/{action_id}/reject")
async def reject_action_endpoint(
    action_id: int,
    body: RejectionRequest,
    db: DBSessionDep,
):
    action = await db.get(AgentAction, action_id)
    if not action:
        raise HTTPException(404, "Not found")
    action.Status = "rejected"
    action.ReviewedBy = body.rejected_by
    action.ReviewedAt = __import__("datetime").datetime.utcnow().isoformat()
    action.ExecutionResult = f"Rejected: {body.reason}"
    await db.commit()
    return {"success": True, "message": "Proposal rejected. No changes made to operational data."}
