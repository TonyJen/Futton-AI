# PROMPT: Build AI-Powered Futon Manufacturing Full-Stack Application

**Role**: You are an expert full-stack software architect and senior engineer specializing in manufacturing ERP systems and production-grade AI agent applications.

**Task**: Build a complete, production-ready, modern full-stack application for **Funton Manufacturing** (a futon and mattress manufacturer) that combines traditional manufacturing ERP capabilities with powerful AI agents.

---

## 1. Tech Stack (Strict)

### Backend
- **Python 3.11+**
- **FastAPI** (latest)
- **SQLAlchemy 2.0** (declarative + async where beneficial) + **aiosqlite**
- **SQLite 3** (primary database — adapt the provided schema)
- **Pydantic v2**
- **Alembic** for migrations
- **LangGraph** (preferred) + **LangChain** for the AI agent layer
- LLM provider abstraction (support OpenAI, Anthropic, Groq, and local Ollama)

### Frontend
- **React 18** + **Vite** + **TypeScript**
- **Tailwind CSS 3.4+**
- **shadcn/ui** (or equivalent Radix + Tailwind components) — professional manufacturing aesthetic
- **TanStack Query (React Query)** v5
- **React Router v6**
- **Recharts** (or Tremor) for all charts and dashboards
- **React Flow** (or @xyflow/react) — for interactive BOM visualization
- **Lucide-react** icons
- **date-fns** + **zod** for forms/validation

### AI / Agents Layer (Critical)
- **LangGraph** for stateful, controllable agent workflows (recommended for manufacturing reliability)
- Tool-calling agents that can safely read the database and propose actions
- Human-in-the-loop approval for high-impact actions (create production order, release PO, change pricing, etc.)
- Persistent agent memory / conversation history (store in SQLite `AgentConversation` and `AgentAction` tables)

### Project Layout (Monorepo)
```
funton-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/                 # config, security, db engine
│   │   ├── db/                   # models (SQLAlchemy), session, seed
│   │   ├── schemas/              # Pydantic request/response
│   │   ├── api/routers/          # FastAPI routers (items, bom, production, sales, agents, reports)
│   │   ├── services/             # Business logic (MRP, costing, inventory, scheduling)
│   │   ├── agents/               # LangGraph agents + tools + supervisor
│   │   │   ├── mrp_agent.py
│   │   │   ├── scheduler_agent.py
│   │   │   ├── inventory_agent.py
│   │   │   ├── sales_pricing_agent.py
│   │   │   ├── quality_agent.py
│   │   │   ├── forecasting_agent.py
│   │   │   └── supervisor.py
│   │   └── utils/
│   ├── alembic/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/                # Dashboard, Items, BOM, Production, Sales, AI Agents, Reports
│   │   ├── lib/api.ts            # typed fetch + TanStack Query hooks
│   │   ├── features/
│   │   └── agents/               # Agent chat UI + agent control panels
│   └── ...
├── data/
│   └── futon_manufacturing_sqlite.sql   # Single-file SQLite schema + seed data
├── docker-compose.yml (optional)
└── README.md
```

---

## 2. Database Requirements

### Source Material
You are given high-quality SQL Server schema + data in the `futon-manufacturing/` folder:
- `01-schema.sql`
- `02-sample-data.sql`
- `05-sales-schema-enhancements.sql`
- `06-sales-sample-data.sql`
- `03-manufacturing-reports.sql` + `07-sales-reports.sql` (40 report views)

### Your Responsibilities
1. **Convert the entire schema to clean, modern SQLite syntax**:
   - `IDENTITY(1,1)` → `INTEGER PRIMARY KEY AUTOINCREMENT`
   - `NVARCHAR` → `TEXT`
   - `DATETIME2` → `TEXT` (store ISO8601) or `TIMESTAMP`
   - Remove `GO` statements and `USE` statements
   - Replace SQL Server computed columns with either:
     - Generated columns (SQLite 3.31+), or
     - Triggers, or (preferred for compatibility) compute in the application layer and store when needed
   - Implement recursive BOM using SQLite recursive CTEs (they work well)
   - Add `FOREIGN KEY` constraints + `PRAGMA foreign_keys = ON`
   - Add proper indexes for performance

2. Create a single consolidated `data/futon_manufacturing_sqlite.sql` file that:
   - Creates all tables
   - Inserts all reference data + sample data (raw materials, components, finished goods, BOMs, inventory, suppliers, customers, sales channels, stores, sales reps, orders, etc.)
   - Includes the most valuable report views adapted to SQLite (prioritize the top 12 manufacturing + top 10 sales reports)

3. Add these new tables for AI agents:
   ```sql
   AgentConversation, AgentAction, AgentRecommendation, AgentAuditLog
   ```

### Key Domain Entities (must support)
- Multi-level BOM (unlimited depth) with scrap rates
- Inventory across multiple warehouses + full transaction history
- Production Orders + material issues + completions
- Purchase Orders + receipts
- Sales Orders (Retail / Online / Wholesale channels) + Quotes + Returns
- Work Centers + capacity planning
- Quality Inspections
- Sales Reps, Territories, Stores, Promotions, Price Lists

---

## 3. AI Agents Specification (The Heart of the Application)

Implement **at minimum 6 specialized agents** orchestrated by a supervisor:

### 1. MRP & Material Planning Agent
- Input: Open production orders + sales forecasts
- Capabilities: Full BOM explosion, net requirements calculation, supplier lead-time awareness, shortage detection
- Output: Recommended purchase orders + suggested production order quantities + timing
- Must propose actions with confidence scores

### 2. Production Scheduler Agent
- Analyzes work center capacity, current WIP, material availability
- Detects bottlenecks
- Proposes feasible production schedule (Gantt-style recommendations)
- Can re-prioritize orders

### 3. Inventory Intelligence Agent
- ABC classification
- Dynamic reorder point / safety stock suggestions using usage patterns
- Dead stock / slow mover identification + disposition recommendations
- Excess inventory alerts

### 4. Sales & Pricing Agent
- Quote generation assistance with margin protection
- Channel-specific pricing recommendations
- Cross-sell / bundle suggestions based on historical product mix
- Discount optimization (what discount level still protects target margin?)

### 5. Quality & Process Agent
- Analyzes inspection data (incoming / in-process / final)
- Identifies patterns in defects by supplier, batch, work center, material
- Root cause hypotheses + recommended corrective actions

### 6. Demand Forecasting + Executive Agent
- Simple statistical forecasting (moving average / exponential smoothing) + LLM narrative
- "What should we build next month?" scenario planning
- Natural language interface to the entire system ("Show me all orders at risk this week and recommend actions")

### Agent Architecture Rules
- Every agent must use **LangGraph** state graphs (not just one-shot ReAct)
- All agents have access to a safe set of **tools**:
  - Read-only query tools (`get_bom_explosion`, `get_inventory_status`, `get_open_production_orders`, etc.)
  - Calculation tools (pure Python MRP engine, cost rollup, etc.)
  - **Action proposal tools** only — never direct writes without human approval
- Every agent action/recommendation must be persisted with full audit trail
- Implement a clean "Agent Action Approval" workflow in both backend and UI

### Agent UI (Critical)
Create a first-class **AI Command Center** page featuring:
- Agent cards with "Launch Agent", "View Recent Runs"
- A unified chat interface (multi-agent capable)
- Clear visualization of proposed actions + Approve / Modify / Reject buttons
- Agent reasoning trace (show the graph steps or tool calls)
- "Explain this recommendation" button

---

## 4. Core Backend API Requirements

Minimum router groups:
- `/api/items`, `/api/bom`
- `/api/inventory`, `/api/transactions`
- `/api/production-orders`, `/api/work-centers`
- `/api/purchase-orders`
- `/api/sales-orders`, `/api/quotes`, `/api/returns`
- `/api/reports` (many endpoints returning the 40+ report datasets)
- `/api/agents` (list agents, run agent, get conversations, approve/reject actions)
- `/api/dashboard` (KPIs + alerts)

Every important domain operation must also be callable by agents via tools.

Implement clean service layer separation — agents should call services, not raw SQL.

---

## 5. Frontend Screens & Experience (Manufacturing-First UX)

### Must-Have Pages
1. **Executive Dashboard**
   - Real-time KPIs: On-time delivery %, inventory value, production utilization, open orders value, critical shortages
   - AI "Recommended Actions" panel (pulls from agents)
   - Charts: Sales by channel (last 12 months), Production output trend, Top 5 shortages

2. **Items & BOM Explorer**
   - Master list with powerful filters (Raw / Component / Finished)
   - Click any finished good → beautiful interactive BOM tree (React Flow)
   - Inline cost roll-up display
   - Ability to edit BOM (with validation)

3. **Inventory Operations**
   - Multi-warehouse view
   - Transaction history
   - "Below Reorder Point" smart table with one-click "Create PO" action

4. **Production Command Center**
   - Current production orders (kanban or table with status)
   - Capacity utilization by work center (visual)
   - Material availability check before releasing orders
   - Record completion + scrap UI

5. **Sales Operations**
   - Multi-channel order pipeline
   - Quote → Order conversion view
   - Returns management
   - Sales rep performance leaderboard

6. **AI Agents Hub** (most important differentiator)
   - Prominent placement
   - Beautiful cards for each agent
   - Live conversation threads
   - Approval queue for agent-proposed actions
   - "Ask anything" natural language bar powered by the supervisor agent

7. **Reports & Analytics**
   - Tabbed interface for Manufacturing Reports vs Sales Reports
   - Export to CSV
   - Date range + filters that actually work

### UI/UX Principles
- Dark/light theme support (manufacturing ops often prefer dark)
- Dense but scannable tables (use tanstack table or shadcn DataTable)
- Excellent empty/loading/error states
- Keyboard-friendly where possible
- Mobile-responsive but optimized for desktop / laptop ops use

---

## 6. Implementation Priorities & Phasing

**Phase 1 (MVP — working in < 2 hours of generation)**
- SQLite schema + seed (full data)
- FastAPI CRUD for core entities + BOM explosion endpoint
- Basic React + Vite app with 3–4 pages (Dashboard, Items, Inventory, Production)
- 2 simple agents (MRP + Inventory) that can read data and propose actions
- One approval workflow fully working end-to-end

**Phase 2**
- Full agent suite + LangGraph supervisor
- Interactive BOM visualizer
- All major reports
- Sales + quoting flows
- Beautiful polished UI

**Phase 3 (Polish)**
- Forecasting models
- PDF generation for quotes / work orders
- Simple authentication (JWT)
- Audit logging everywhere

---

## 7. Non-Functional & Quality Requirements

- Strong typing end-to-end (Pydantic + TypeScript interfaces generated or manually synced)
- Proper error handling + validation on every boundary
- Clear README with:
  - `cd backend && python -m venv .venv && pip install -r requirements.txt`
  - `alembic upgrade head`
  - `python -m app.db.seed` (or similar)
  - `uvicorn app.main:app --reload`
  - `cd frontend && npm install && npm run dev`
- Environment variable driven LLM configuration
- No hardcoded secrets
- Good logging (especially for agent tool calls and decisions)
- Seed script must be idempotent / safe to re-run

---

## 8. Output Deliverables Expected

When you finish, the generated project must allow a developer to:
1. Run one SQL file to get a fully populated manufacturing database
2. Start the backend and have all core + AI endpoints functional
3. Start the frontend and have a professional, usable manufacturing + AI system
4. Immediately interact with at least the MRP and Inventory agents and approve real actions that affect the database

---

## 9. Reference Material

All source SQL files live in the sibling `futon-manufacturing/` directory (relative to where this prompt will be used). Use them as the single source of truth for domain model, sample data volume, and report semantics.

**Begin work.** Produce clean, maintainable, well-structured code with excellent comments only where they add value. Prioritize getting the AI agents working with real data and a smooth approval loop — that is the unique value of this system.

---

**End of Prompt**

Copy everything above this line when feeding to an AI coding assistant (Claude, Cursor, GPT-4o, Grok, etc.).
