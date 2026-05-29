"""
AgentState definition for LangGraph agents.

This is the shared state passed between nodes in the StateGraph.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict, total=False):
    """Shared state for all manufacturing agents."""

    # Identity
    run_id: str
    agent_name: str
    conversation_id: Optional[int]

    # Input
    input_params: Dict[str, Any]

    # Observability
    reasoning_trace: List[str]
    tool_calls: List[Dict[str, Any]]

    # Working data
    current_data: Dict[str, Any]

    # Output
    proposals: List[Dict[str, Any]]   # list of {"action_id": int, ...}
    recommendations: List[Dict[str, Any]]

    # Control
    status: str   # running | completed | failed


def create_initial_state(
    agent_name: str,
    input_params: Optional[Dict[str, Any]] = None,
    run_id: Optional[str] = None,
) -> AgentState:
    """Factory for a fresh agent state."""
    import uuid
    return {
        "run_id": run_id or str(uuid.uuid4()),
        "agent_name": agent_name,
        "input_params": input_params or {},
        "reasoning_trace": [],
        "tool_calls": [],
        "current_data": {},
        "proposals": [],
        "recommendations": [],
        "status": "running",
    }


def append_reasoning_step(state: AgentState, message: str, **extra: Any) -> None:
    """Helper to append a step to the reasoning trace."""
    entry = {"message": message, **extra}
    state.setdefault("reasoning_trace", []).append(str(entry))
