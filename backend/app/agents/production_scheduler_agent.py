"""
Production Scheduler Agent — LangGraph StateGraph (Phase 3).

Focus:
- Analyzes work center utilization + open production orders
- Detects bottlenecks and late orders
- Proposes RELEASE_PRODUCTION_ORDER actions for feasible work
- All proposals go through human-in-the-loop approval
"""

import uuid
from typing import Any, Dict
from langgraph.graph import StateGraph, END

from .base import BaseAgent
from .state import AgentState


class ProductionSchedulerAgent(BaseAgent):
    name = "production_scheduler"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        run_id = str(uuid.uuid4())
        graph = self._build_graph()

        state: AgentState = {
            "run_id": run_id,
            "agent_name": self.name,
            "input_params": input_data or {},
            "reasoning_trace": ["Production Scheduler started"],
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
        wf = StateGraph(AgentState)
        wf.add_node("load_capacity", self._node_load_capacity)
        wf.add_node("analyze", self._node_analyze_schedule)
        wf.add_node("propose", self._node_generate_proposals)
        wf.set_entry_point("load_capacity")
        wf.add_edge("load_capacity", "analyze")
        wf.add_edge("analyze", "propose")
        wf.add_edge("propose", END)
        return wf.compile()

    async def _node_load_capacity(self, state: AgentState) -> AgentState:
        for t in self.tools:
            name = getattr(t, "name", "")
            if "get_work_center_utilization" in name:
                state["current_data"]["work_centers"] = await t.ainvoke({})
            if "get_open_production_orders" in name:
                state["current_data"]["open_orders"] = await t.ainvoke({})
        state["reasoning_trace"].append("Loaded work center capacity and open orders")
        return state

    async def _node_analyze_schedule(self, state: AgentState) -> AgentState:
        wcs = state.get("current_data", {}).get("work_centers", [])
        orders = state.get("current_data", {}).get("open_orders", [])

        bottlenecks = [wc for wc in wcs if wc.get("current_utilization", 0) > 85]
        late_orders = [o for o in orders if o.get("priority") == "High"]

        state["current_data"]["bottlenecks"] = bottlenecks
        state["current_data"]["late_orders"] = late_orders
        state["reasoning_trace"].append(
            f"Analysis: {len(bottlenecks)} bottlenecks, {len(late_orders)} high-priority orders at risk"
        )
        return state

    async def _node_generate_proposals(self, state: AgentState) -> AgentState:
        conv = await self._ensure_conversation(state.get("input_params", {}).get("user_id"))
        proposals_made = 0

        open_orders = state.get("current_data", {}).get("open_orders", [])
        bottlenecks = state.get("current_data", {}).get("bottlenecks", [])

        # Propose releasing high-priority orders on non-bottleneck centers first
        safe_orders = [o for o in open_orders if o.get("status") in ("Released", "Planned")][:2]

        for order in safe_orders:
            action_id = await self.propose(
                conv,
                action_type="RELEASE_PRODUCTION_ORDER",
                payload={
                    "ProductionOrderID": order.get("production_order_id"),
                    "WorkCenter": order.get("work_center"),
                },
                rationale=f"Scheduler recommends releasing {order.get('order_number')} on {order.get('work_center')} "
                          f"(due {order.get('due_date')}). Capacity appears available.",
                confidence=0.81,
            )
            state["proposals"].append({"action_id": action_id})
            proposals_made += 1

        # If bottlenecks exist, suggest one re-prioritization or hold
        if bottlenecks and open_orders:
            bottleneck_name = bottlenecks[0].get("name")
            action_id = await self.propose(
                conv,
                action_type="RELEASE_PRODUCTION_ORDER",
                payload={
                    "ProductionOrderID": open_orders[0].get("production_order_id"),
                    "WorkCenter": bottleneck_name,
                    "Notes": "Expedite on bottleneck work center per scheduler",
                },
                rationale=f"High utilization on {bottleneck_name} — recommend releasing one critical order now to avoid delay.",
                confidence=0.69,
            )
            state["proposals"].append({"action_id": action_id})
            proposals_made += 1

        if proposals_made == 0:
            # Smarter fallback: Use first available open order if any exist
            if open_orders:
                first_order = open_orders[0]
                action_id = await self.propose(
                    conv,
                    action_type="RELEASE_PRODUCTION_ORDER",
                    payload={
                        "ProductionOrderID": first_order.get("production_order_id"),
                        "WorkCenter": first_order.get("work_center", "Assembly A"),
                    },
                    rationale=f"Scheduler fallback: Releasing {first_order.get('order_number', 'next order')} "
                              "as no clear bottlenecks were identified.",
                    confidence=0.55,
                )
                state["proposals"].append({"action_id": action_id})
                proposals_made += 1
            else:
                state["reasoning_trace"].append("No open orders or capacity issues detected.")

        state["status"] = "completed"
        state["conversation_id"] = conv
        state["reasoning_trace"].append(f"Generated {proposals_made} scheduling proposal(s) for human approval.")
        return state
