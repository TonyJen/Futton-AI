"""
Inventory Intelligence Agent — StateGraph implementation.
"""

import uuid
from typing import Any, Dict

from langgraph.graph import END, StateGraph

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

        # Add better diagnostic reasoning
        shortages = state["current_data"].get("shortages", [])
        abc = state["current_data"].get("abc", [])
        a_count = sum(1 for x in abc if x.get("class") == "A")

        state["reasoning_trace"].append(
            f"Analysis complete: {len(shortages)} items below reorder point. "
            f"ABC breakdown: {a_count} Class A items identified."
        )
        return state

    async def _node_propose(self, state: AgentState):
        conv = await self._ensure_conversation(state.get("input_params", {}).get("user_id"))

        shortages = state.get("current_data", {}).get("shortages", [])
        abc_data = state.get("current_data", {}).get("abc", [])
        proposals_made = 0

        # Build a quick lookup for ABC class
        abc_lookup = {item["item_id"]: item for item in abc_data}

        # Prioritize shortages: A-class items first, then by severity of shortage
        def shortage_priority(item):
            abc_info = abc_lookup.get(item.get("item_id"), {})
            abc_weight = {"A": 3, "B": 2, "C": 1}.get(abc_info.get("class"), 1)
            return abc_weight * 100 + item.get("shortage", 0)

        prioritized_shortages = sorted(shortages, key=shortage_priority, reverse=True)

        for item in prioritized_shortages[:3]:  # Top 3 after prioritization
            item_id = item.get("item_id")
            abc_info = abc_lookup.get(item_id, {})
            abc_class = abc_info.get("class", "C")
            shortage_qty = item.get("shortage", 0)

            # Dynamic reorder point increase based on ABC class
            multiplier = 1.5 if abc_class == "A" else (1.35 if abc_class == "B" else 1.2)
            new_reorder = max(
                int(item.get("reorder_point", 100) * 1.1),
                int(shortage_qty * multiplier)
            )

            # Dynamic confidence based on data quality
            confidence = 0.88 if abc_class == "A" else (0.78 if abc_class == "B" else 0.68)

            rationale = (
                f"Inventory Intelligence detected a shortage of {shortage_qty:.0f} units for "
                f"{item.get('item_name', 'item')} (Class {abc_class}). "
                f"Recommending increase of reorder point to {new_reorder} to reduce stockout risk."
            )

            action_id = await self.propose(
                conv,
                action_type="UPDATE_REORDER_POINT",
                payload={
                    "ItemID": item_id,
                    "NewReorderPoint": new_reorder,
                },
                rationale=rationale,
                confidence=confidence,
            )
            state["proposals"].append({"action_id": action_id})
            proposals_made += 1
            state["reasoning_trace"].append(
                f"Proposed reorder point increase for {item.get('item_name')} (Class {abc_class})"
            )

        if proposals_made == 0:
            # Smarter fallback: look for high-value C-class items that might benefit from review
            high_value_c_items = [
                item for item in abc_data
                if item.get("class") == "C" and item.get("inventory_value", 0) > 5000
            ][:1]

            if high_value_c_items:
                item = high_value_c_items[0]
                action_id = await self.propose(
                    conv,
                    action_type="REVIEW_REORDER_POINT",
                    payload={"ItemID": item["item_id"]},
                    rationale=f"High inventory value ({item['inventory_value']}) on Class C item. "
                              "Suggest reviewing whether current reorder point is appropriate.",
                    confidence=0.55,
                )
                state["proposals"].append({"action_id": action_id})
                proposals_made += 1
            else:
                state["reasoning_trace"].append("No actionable inventory issues found at this time.")

        state["status"] = "completed"
        state["conversation_id"] = conv
        state["reasoning_trace"].append(f"Created {proposals_made} inventory optimization proposal(s).")
        return state
