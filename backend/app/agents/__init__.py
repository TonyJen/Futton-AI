"""
Funton AI Agents Package — Phase 1 (LangGraph + HITL)

Exports the two production agents.
"""

from .mrp_agent import MRPPlanningAgent
from .inventory_agent import InventoryIntelligenceAgent

__all__ = [
    "MRPPlanningAgent",
    "InventoryIntelligenceAgent",
]
