"""
MRP & Material Planning Agent — Full LangGraph StateGraph (Phase 1).

Uses explicit nodes for:
- BOM explosion
- Shortage detection (via tools)
- Proposal generation (PO / Production Order)
- Persist as "proposed" via approval layer (never direct write)
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List

from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseAgent
from .state import AgentState


class MRPPlanningAgent(BaseAgent):
    name = "mrp"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Entry point used by router."""
        run_id = str(uuid.uuid4())
        graph = self._build_graph()

        state: AgentState = {
            "run_id": run_id,
            "agent_name": self.name,
            "input_params": input_data or {},
            "reasoning_trace": ["MRP Agent invoked"],
            "tool_calls": [],
            "current_data": {},
            "proposals": [],
            "status": "running",
        }

        final = await graph.ainvoke(state)
        return {
            "run_id": run_id,
            "agent_name": self.name,
            "status": final.get("status", "completed"),
            "proposals_created": len(final.get("proposals", [])),
            "reasoning_trace": final.get("reasoning_trace", []),
            "conversation_id": final.get("conversation_id"),
        }

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)

        workflow.add_node("explode", self._node_explode_bom)
        workflow.add_node("shortages", self._node_detect_shortages)
        workflow.add_node("propose", self._node_generate_and_persist)

        workflow.set_entry_point("explode")
        workflow.add_edge("explode", "shortages")
        workflow.add_edge("shortages", "propose")
        workflow.add_edge("propose", END)

        return workflow.compile()

    async def _node_explode_bom(self, state: AgentState) -> AgentState:
        item_id = state["input_params"].get("item_id")
        if not item_id:
            state["reasoning_trace"].append("No item_id — skipping detailed explosion (will use open orders)")
            return state

        # Use one of the tools (they return JSON strings)
        for t in self.tools:
            if "explode_bill_of_materials" in getattr(t, "name", ""):
                raw = await t.ainvoke({"item_id": item_id, "quantity": state["input_params"].get("quantity", 1)})
                state["current_data"]["bom"] = raw
                state["reasoning_trace"].append(f"BOM exploded for item {item_id}")
                break
        return state

    async def _node_detect_shortages(self, state: AgentState) -> AgentState:
        for t in self.tools:
            if "find_low_stock_and_shortages" in getattr(t, "name", ""):
                raw = await t.ainvoke({"threshold_multiplier": 1.0})
                state["current_data"]["shortages"] = raw
                state["reasoning_trace"].append(f"Shortage detection complete — {len(raw)} items at risk")
                break

        # Also run ABC for better prioritization in propose step
        for t in self.tools:
            if "run_abc_analysis" in getattr(t, "name", ""):
                abc = await t.ainvoke({})
                state["current_data"]["abc"] = abc
                break

        return state

    async def _node_generate_and_persist(self, state: AgentState) -> AgentState:
        conv_id = await self._ensure_conversation(state["input_params"].get("user_id"))
        proposals_made = 0

        shortages = state.get("current_data", {}).get("shortages", [])
        bom_data = state.get("current_data", {}).get("bom", {})

        # Smarter proposal generation using ABC classification when available
        abc_lookup = {item["item_id"]: item for item in state.get("current_data", {}).get("abc", [])}

        if shortages:
            # Prioritize A-class items
            def priority(s):
                abc = abc_lookup.get(s.get("item_id"), {})
                weight = {"A": 3, "B": 2, "C": 1}.get(abc.get("class"), 1)
                return weight * 100 + s.get("shortage", 0)

            prioritized = sorted(shortages, key=priority, reverse=True)

            for shortage in prioritized[:3]:
                item_id = shortage.get("item_id")
                shortage_qty = shortage.get("shortage", 100)
                abc_class = abc_lookup.get(item_id, {}).get("class", "C")

                # More aggressive replenishment for A-class items
                multiplier = 2.0 if abc_class == "A" else 1.5
                recommended_qty = max(100, int(shortage_qty * multiplier))

                confidence = 0.87 if abc_class == "A" else 0.78

                action_id = await self.propose(
                    conv_id,
                    action_type="CREATE_PURCHASE_ORDER",
                    payload={
                        "ItemID": item_id,
                        "Quantity": recommended_qty,
                        "WarehouseID": state["input_params"].get("warehouse_id", 1),
                    },
                    rationale=f"MRP detected shortage of {shortage.get('item_name', 'component')} "
                              f"({shortage_qty:.0f} units below reorder point, Class {abc_class}). "
                              f"Recommending {recommended_qty} units replenishment.",
                    confidence=confidence,
                )
                state["proposals"].append({"action_id": action_id})
                proposals_made += 1
        else:
            # Improved fallback: Try to find the highest value item from ABC analysis if available
            abc_data = state.get("current_data", {}).get("abc", [])
            if abc_data:
                # Pick the top A-class item, or highest scoring item
                top_item = next((i for i in abc_data if i.get("class") == "A"), abc_data[0])
                item_id = top_item["item_id"]
                rationale = f"MRP fallback: Recommending safety stock for high-priority item {top_item.get('item_name', item_id)} based on ABC analysis."
            else:
                item_id = state["input_params"].get("item_id", 1)
                rationale = "MRP analysis recommends safety stock replenishment based on BOM requirements."

            action_id = await self.propose(
                conv_id,
                action_type="CREATE_PURCHASE_ORDER",
                payload={
                    "ItemID": item_id,
                    "Quantity": state["input_params"].get("quantity", 150),
                    "WarehouseID": state["input_params"].get("warehouse_id", 1),
                },
                rationale=rationale,
                confidence=0.62,
            )
            state["proposals"].append({"action_id": action_id})
            proposals_made += 1

        state["conversation_id"] = conv_id
        state["status"] = "completed"
        state["reasoning_trace"].append(
            f"Created {proposals_made} proposal(s) with status='proposed'. Awaiting human approval."
        )
        return state
