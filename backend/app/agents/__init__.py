"""
Funton AI Agents Package — Phase 1 (LangGraph + HITL)

Exports the two production agents.
"""

from .inventory_agent import InventoryIntelligenceAgent
from .mrp_agent import MRPPlanningAgent

__all__ = [
    "MRPPlanningAgent",
    "InventoryIntelligenceAgent",
]
