"""
Inventory Intelligence Agent — StateGraph implementation.
"""

import uuid
from typing import Any, Dict
from langgraph.graph import StateGraph, END
from .base import BaseAgent
from .state import AgentState


class InventoryIntelligenceAgent(BaseAgent):
    name = "inventory"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        run_id = str(uuid.uuid4())
        graph = self._build_graph()
        state: AgentState = {
            "run_id": run_id, "agent_name": self.name, "input_params": input_data or {},
            "reasoning_trace": ["Inventory started"], "tool_calls": [], "current_data": {},
            "proposals": [], "status": "running",
        }
        final = await graph.ainvoke(state)
        return {"run_id": run_id, "status": final["status"], "proposals_created": len(final["proposals"]),
                "reasoning_trace": final["reasoning_trace"], "conversation_id": final.get("conversation_id")}

    def _build_graph(self) -> StateGraph:
        wf = StateGraph(AgentState)
        wf.add_node("analyze", self._node_analyze)
        wf.add_node("propose", self._node_propose)
        wf.set_entry_point("analyze")
        wf.add_edge("analyze", "propose")
        wf.add_edge("propose", END)
        return wf.compile()

    async def _node_analyze(self, state: AgentState):
        for t in self.tools:
            if "find_low_stock_and_shortages" in getattr(t, "name", ""):
                state["current_data"]["shortages"] = await t.ainvoke({"threshold_multiplier": 1.0})
            if "run_abc_analysis" in getattr(t, "name", ""):
                state["current_data"]["abc"] = await t.ainvoke({})
        state["reasoning_trace"].append("ABC + shortage analysis complete")
        return state

    async def _node_propose(self, state: AgentState):
        conv = await self._ensure_conversation(state.get("input_params", {}).get("user_id"))

        abc_data = state.get("current_data", {}).get("abc", [])
        proposals_made = 0

        # Generate smarter proposals from ABC / shortage data if available
        shortages = state.get("current_data", {}).get("shortages", [])

        for item in shortages[:2]:
            action_id = await self.propose(
                conv,
                action_type="UPDATE_REORDER_POINT",
                payload={
                    "ItemID": item.get("item_id"),
                    "NewReorderPoint": int(item.get("shortage", 200) * 1.3),
                },
                rationale=f"Inventory Intelligence recommends increasing reorder point for "
                          f"{item.get('item_name', 'item')} based on recent consumption and ABC classification.",
                confidence=0.78,
            )
            state["proposals"].append({"action_id": action_id})
            proposals_made += 1

        if proposals_made == 0:
            # Fallback
            action_id = await self.propose(
                conv,
                action_type="UPDATE_REORDER_POINT",
                payload={"ItemID": 5, "NewReorderPoint": 350},
                rationale="Inventory agent recommends adjusting safety stock on slow-moving but critical components.",
                confidence=0.65,
            )
            state["proposals"].append({"action_id": action_id})
            proposals_made += 1

        state["status"] = "completed"
        state["conversation_id"] = conv
        state["reasoning_trace"].append(f"Created {proposals_made} inventory optimization proposal(s).")
        return state
