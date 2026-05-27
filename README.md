# Funton AI

**AI-Powered Futon Manufacturing ERP System**

Funton AI is a modern, full-stack manufacturing execution platform built for a futon and mattress manufacturer. It combines traditional ERP capabilities with intelligent LangGraph agents that assist with material planning, inventory optimization, and decision support — all under human oversight.

---

## Features

### Core ERP Capabilities
- **Multi-level Bill of Materials (BOM)** with recursive explosion and scrap tracking
- **Inventory Management** across multiple warehouses with full transaction history
- **Production Orders** — planning, material allocation, and completion recording
- **Sales & Purchasing** — orders, quotes, returns, and supplier management
- **Quality & Reporting** — rich views for shortages, capacity, costing, and performance

### AI Agents (LangGraph + Human-in-the-Loop)
- **MRP Planning Agent** — analyzes BOMs and inventory to propose purchase orders and production adjustments
- **Inventory Intelligence Agent** — performs ABC analysis, detects slow movers, and recommends dynamic reorder points
- **Proposal-Only Design** — agents never execute actions directly. All suggestions go through an explicit approval queue.
- **Action Executor** — the single place where approved actions become real database changes (POs, inventory adjustments, reorder point updates)
- **Full Observability** — every agent run produces a detailed reasoning trace

### Modern Full-Stack Experience
- Clean React + Vite frontend with a dedicated **AI Agents Hub**
- Professional manufacturing-grade UI (dense tables, KPI cards, approval workflows)
- Real-time proposal queue and one-click approve/reject
- Responsive design with excellent empty/loading states

---

## Architecture

```
┌─────────────────────┐
│   React + Vite      │  ← Frontend (Agents Hub, Dashboards, BOM Explorer)
│   (TypeScript)      │
└──────────┬──────────┘
           │ REST /api/v1
┌──────────▼──────────┐
│   FastAPI Backend   │
│   (Python)          │
│                     │
│  ┌───────────────┐  │
│  │  Routers      │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │   Services    │  │  ← Business logic (BOM, Inventory, Executor)
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ LangGraph     │  │  ← AI Agents (MRP + Inventory)
│  │   Agents      │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │  SQLAlchemy   │  │
│  │   + SQLite    │  │
│  └───────────────┘  │
└─────────────────────┘
```

### Agent Decision Flow (Text Sequence Diagram)

```
User / Frontend
      │
      │ 1. POST /agents/run { "agent_name": "mrp", "params": {...} }
      ▼
Agents Router
      │
      │ 2. Instantiate MRPPlanningAgent
      ▼
LangGraph Graph
      │
      ├─── explode_bom (calls tools)
      │
      ├─── detect_shortages (calls tools)
      │
      └─── generate_proposals
            │
            └─── propose_action()  →  INSERT AgentAction (status='proposed')
            │
            └─── INSERT AgentAuditLog
            │
      Return { run_id, proposals_created, reasoning_trace }
      │
      ▼
Frontend AI Hub
      │
      │ 3. GET /agents/proposals  →  Shows pending queue
      │
      │ 4. Human clicks "Approve"
      │
      ▼
POST /agents/actions/{id}/approve
      │
      │ 5. Load AgentAction
      │ 6. Call ActionExecutor.execute_proposal()
      │     └── Creates real PurchaseOrder / InventoryTransaction / etc.
      │
      │ 7. Update AgentAction → status='executed'
      │ 8. Write audit log
      │
      ▼
Response: { success: true, execution_details: ... }
```

---

## Features

- **Intelligent Agents** — Two production-grade LangGraph agents with rich reasoning traces
- **Safe AI Execution** — Strict propose-only model with mandatory human approval
- **Rich Manufacturing Data Model** — 30+ tables including multi-level BOM, multi-warehouse inventory, production, sales, and agent audit tables
- **Beautiful Operations UI** — Dense, professional interface designed for real factory use
- **Full Observability** — Every agent decision is logged with tool calls and thoughts
- **Extensible Architecture** — Clean service layer makes it easy to add more agents (Scheduler, Quality, Pricing, etc.)

---

## Get Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- SQLite (comes with Python)

### 1. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Windows PowerShell
# source .venv/bin/activate           # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create environment file (add your LLM keys if using full tool-calling later)
copy .env.example .env

# Seed the database (creates data/futon_manufacturing.db with full schema + realistic sample data)
python -m app.db.seed

# Run the API
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000/docs`.

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173`.

### 3. Try the AI Agents

1. Open the frontend and go to the **Agents** tab (AI Command Center)
2. Click **Run** on the MRP Agent or Inventory Intelligence Agent
3. Go to the proposal queue
4. Approve or reject the generated recommendations
5. Watch real data change in the system (new POs, updated reorder points, inventory transactions)

---

## Tech Stack

**Backend**
- FastAPI + SQLAlchemy 2.0 (async)
- LangGraph + LangChain (agents)
- SQLite (aiosqlite)
- Pydantic v2
- Alembic

**Frontend**
- React 18 + Vite + TypeScript
- TanStack Query
- Tailwind + custom manufacturing UI components
- Recharts (visualizations)
- React Flow (future BOM visualization)

**AI / Agents**
- LangGraph StateGraphs (not simple ReAct)
- Human-in-the-loop approval workflow
- Structured reasoning traces

---

## Project Structure

```
Funton-Ai/
├── backend/
│   ├── app/
│   │   ├── agents/           # LangGraph agents + tools + approval layer
│   │   ├── api/routers/      # FastAPI endpoints
│   │   ├── services/         # Business logic (BOM, Executor, etc.)
│   │   ├── db/               # Models + session
│   │   └── core/             # Config + dependencies
│   ├── tests/                # Pytest suite
│   └── data/                 # SQLite database + seed script
├── frontend/
│   ├── src/
│   │   ├── pages/            # Dashboard, Agents, Inventory, etc.
│   │   └── components/       # Manufacturing UI + AI components
│   └── vitest.config.ts      # Frontend tests
├── data/
│   └── futon_manufacturing_sqlite.sql   # Source-of-truth schema + data
├── futon-manufacturing/      # Original reference SQL Server schemas
└── prompt.md                 # Original project specification
```

---

## Testing

**Backend**
```bash
cd backend
pytest tests/ -v
```

**Frontend**
```bash
cd frontend
npm test
```

---

## License

Internal project / Educational use.

---

Built as a demonstration of production-grade AI agents in a real manufacturing domain with strict safety controls (human-in-the-loop execution).
