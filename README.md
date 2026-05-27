# Funton AI

**AI-Powered Futon Manufacturing ERP System**

Funton AI is a modern, full-stack manufacturing execution platform built for a futon and mattress manufacturer. It combines traditional ERP capabilities with intelligent LangGraph agents that assist with material planning, inventory optimization, and decision support — all under human oversight.

**The highlight** is the **AI Supervisor** — a conversational interface powered by a real LLM (xAI Grok by default) that can analyze your business and intelligently trigger specialized agents through natural language.

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
┌──────────────────────────────────────┐
│   React + Vite (TypeScript)          │
│   • Dashboards & Operations UI       │
│   • AI Supervisor Chat  ← (LLM)      │
│   • Agent Cards + Approval Queue     │
│   • Interactive BOM Visualizer       │
└───────────────────┬──────────────────┘
                    │ REST /api/v1
┌───────────────────▼──────────────────┐
│            FastAPI Backend           │
│                                      │
│  ┌────────────────────────────────┐  │
│  │           Routers              │  │
│  │  • /agents                     │  │
│  │  • /agents/supervisor/chat     │  │  ← New conversational endpoint
│  │  • /sales, /purchasing, etc.   │  │
│  └───────────────┬────────────────┘  │
│                  │                   │
│  ┌───────────────▼───────────────┐   │
│  │          Services             │   │
│  │  • Agent Service              │   │
│  │  • Supervisor Service (LLM)   │   │
│  │  • Action Executor            │   │
│  └───────────────┬───────────────┘   │
│                  │                   │
│  ┌───────────────▼───────────────┐   │
│  │         AI Layer              │   │
│  │  • LangGraph Agents (3)       │   │
│  │    - MRP Planning             │   │
│  │    - Inventory Intelligence   │   │
│  │    - Production Scheduler     │   │
│  │  • AI Supervisor (xAI/Grok)   │   │  ← Conversational LLM
│  └───────────────┬───────────────┘   │
│                  │                   │
│  ┌───────────────▼───────────────┐   │
│  │   SQLAlchemy 2.0 + SQLite     │   │
│  └───────────────────────────────┘   │
└──────────────────────────────────────┘
```

### Agent Decision Flow

There are now **two main ways** to interact with agents:

#### A. Traditional (Direct Agent Execution)
```
User → Click "Run" on Agent Card
   → POST /agents/run
   → LangGraph Agent runs
   → Proposals saved with status='proposed'
   → Appear in Approval Queue
   → Human Approves → ActionExecutor runs real changes
```

#### B. Conversational (AI Supervisor) ← Recommended
```
User chats with AI Supervisor (real LLM)
   → Supervisor analyzes business state
   → Suggests relevant agent(s)
   → User says "yes run the inventory agent"
   → Frontend triggers the agent(s)
   → Proposals appear in queue for approval
   → Same execution path as above
```

Both paths feed into the same **Action Executor**, ensuring all AI-proposed changes go through human review.

---

## Features

- **Intelligent Agents** — Three production-grade LangGraph agents (MRP, Inventory Intelligence, Production Scheduler)
- **Conversational AI Supervisor** — Real LLM (xAI Grok by default) that can analyze the business and intelligently trigger agents via natural language
- **Safe AI Execution** — Strict propose-only model with mandatory human approval (nothing executes without explicit user consent)
- **Rich Manufacturing Data Model** — 30+ tables including multi-level BOM, multi-warehouse inventory, production, sales, purchasing, and full agent audit history
- **Beautiful Operations UI** — Dense, professional manufacturing-grade interface
- **Full Observability** — Every agent decision includes detailed reasoning traces and tool calls
- **Extensible Architecture** — Clean service layer designed to easily add more agents and capabilities

---

## Get Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- SQLite (included with Python)

### One-Command Start (Recommended)

The easiest way to run everything:

```powershell
# Windows
.\start.ps1
```

This script will:
- Activate the root virtual environment
- Install backend & frontend dependencies if missing
- Seed the database
- Start the FastAPI backend (in a new window)
- Start the React frontend

**Important:** The AI Supervisor uses a real LLM. You will need an API key (xAI recommended).

### Manual Setup

#### 1. Backend

```bash
# Create and activate virtual environment (at project root)
python -m venv .venv
.\.venv\Scripts\Activate.ps1     # Windows
# source .venv/bin/activate      # macOS/Linux

# Install dependencies
pip install -r backend/requirements.txt

# Copy environment file
cp backend/.env.example backend/.env
# or on Windows: copy backend\.env.example backend\.env
```

Edit `backend/.env` and add your LLM key (required for the AI Supervisor):

```env
DEFAULT_LLM_PROVIDER=xai
XAI_API_KEY=xai-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Seed the database and start the backend:

```bash
python data/seed.py
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`.

### 3. Best Experience: Follow the Guided Demo

For the most impressive walkthrough (especially the AI Supervisor), see:

→ **[DEMO.md](./DEMO.md)** — A step-by-step script showing natural language control of agents and real business impact.

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
- 3 LangGraph Agents (MRP, Inventory Intelligence, Production Scheduler)
- AI Supervisor — Real LLM (xAI Grok by default) with conversational agent orchestration
- Human-in-the-loop approval workflow
- Full reasoning traces + audit logging

---

## Project Structure

```
Funton-Ai/
├── backend/
│   ├── app/
│   │   ├── agents/           # LangGraph agents + Supervisor service
│   │   ├── api/routers/      # FastAPI endpoints (incl. /supervisor/chat)
│   │   ├── services/         # Business logic + Action Executor
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
