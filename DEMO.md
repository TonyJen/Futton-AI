# Funton AI - Guided Demo Script

This document provides a step-by-step walkthrough to experience the best parts of Funton AI, especially the **AI Supervisor** — the most impressive feature of the project.

## Prerequisites

- You have successfully started the app using `.\start.ps1` (or manually)
- The backend is running on `http://localhost:8000`
- The frontend is running on `http://localhost:5173`
- You have configured a valid LLM key (xAI recommended) so the Supervisor works with real intelligence

---

## Step-by-Step Demo

### 1. Open the Application

Go to: [http://localhost:5173](http://localhost:5173)

You should see the **Dashboard** with KPIs, charts, and pending AI recommendations.

### 2. Navigate to the AI Agents Hub

Click on **AI Agents Hub** in the sidebar.

You will see:
- The **AI Supervisor** chat interface at the top (this is the star of the show)
- Three agent cards below (MRP, Inventory Intelligence, Production Scheduler)
- An Approval Queue showing pending proposals

### 3. Talk to the AI Supervisor

This is the most impressive part. The Supervisor is powered by a real LLM (xAI Grok by default) and has context about your manufacturing business.

**Try these prompts in order:**

#### Prompt 1: General Awareness
```
What should we focus on right now?
```

Expected behavior:
- The Supervisor analyzes current data (inventory, capacity, demand)
- It suggests 1–2 agents that would be most useful

#### Prompt 2: Take Action
After it suggests an agent (for example Inventory Intelligence), reply:

```
yes run the inventory agent
```

or simply:

```
yes
```

**What should happen:**
- The frontend detects your intent
- It automatically triggers the Inventory Intelligence Agent
- New proposals appear in the **Approval Queue**

#### Prompt 3: Multi-Agent Coordination (Most Impressive)
Ask a broader question:

```
what is the health of my business?
```

The Supervisor will likely recommend multiple agents. Reply with:

```
yes trigger both
```

or

```
yes run them
```

**What should happen:**
- Both the Inventory Intelligence Agent **and** the Production Scheduler Agent will be triggered
- Multiple new proposals will appear in the queue

### 4. Review & Approve Proposals

In the **Approval Queue** section:

- Click **Approve** on one or more proposals
- Watch the system execute real changes:
  - New Purchase Orders being created
  - Inventory levels updating
  - Reorder points being adjusted

You can also click **Reject** to see that no changes are made.

### 5. Explore Other Areas (Optional but Recommended)

- Go to **Purchasing** → See real POs and try receiving goods
- Go to **Quotes** → Create a quote and convert it to an order
- Go back to **Dashboard** → Watch the KPIs and recommendation count update

---

## Key Things to Highlight

When showing this demo to someone, emphasize these points:

1. **The Supervisor is not a toy** — It is powered by a real LLM and can reason about your actual business data.
2. **Human-in-the-loop is enforced** — Agents only *propose*. Nothing changes without explicit human approval.
3. **Actions have real consequences** — Approving a proposal actually creates POs, adjusts inventory, etc.
4. **Natural language control** — You can coordinate multiple specialized agents just by chatting.

---

## Troubleshooting During Demo

| Problem | Solution |
|--------|----------|
| Supervisor says it's in simulation mode | Check that `XAI_API_KEY` (or other LLM key) is correctly set in `backend/.env` and restart backend |
| "I couldn't connect to the AI Supervisor" | Backend is not running. Restart using `start.ps1` or manually |
| Agents not appearing after saying "yes" | Hard refresh the page (Ctrl+Shift+R). The recommendations query may need to refetch |
| 404 errors on agent runs | Make sure you restarted the backend after recent route updates |

---

## Suggested Demo Flow (5–7 minutes)

1. Open Dashboard → Show live data + pending recommendations
2. Go to AI Agents Hub
3. Ask Supervisor: *"What should we focus on right now?"*
4. Say: *"yes trigger both"*
5. Show new proposals appearing
6. Approve 1–2 proposals and show real data changes
7. (Bonus) Go to Purchasing and show a newly created PO from the agent

This flow usually impresses people because they see **natural language → intelligent agent coordination → real business impact** in under a minute.

---

**Enjoy the demo!** This project was built to show what responsible, controllable AI agents can look like in a real operational system.
