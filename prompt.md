# Build an AI-Powered Futon Manufacturing ERP System

**Role**: You are an elite full-stack engineer and AI systems architect. Build a complete, modern, production-quality application for Funton Manufacturing (a real futon and mattress manufacturer).

The system must combine traditional manufacturing ERP functionality with powerful, controllable AI agents that help run the factory.

---

## Tech Stack (Use Exactly This)

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 + aiosqlite
- SQLite (primary database)
- Pydantic v2
- Alembic (migrations)
- LangGraph + LangChain (for agents)
- Support multiple LLMs via environment variables (OpenAI, Anthropic, Groq, Ollama)

### Frontend
- React 18 + Vite + TypeScript
- Tailwind CSS + shadcn/ui (or equivalent high-quality components)
- TanStack Query v5
- React Router v6
- Recharts (charts)
- React Flow / @xyflow/react (for interactive BOM visualization)
- Lucide icons + date-fns + zod

### AI Agents
- LangGraph (stateful graphs, not simple ReAct)
- Human-in-the-loop approval for all actions that change data
- Persistent agent memory and action history stored in SQLite

---

## Project Structure

```
funton-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   ├── db/               # SQLAlchemy models + seed logic
│   │   ├── schemas/          # Pydantic models
│   │   ├── api/routers/
│   │   ├── services/         # Core business logic (MRP, costing, etc.)
│   │   └── agents/           # All LangGraph agents live here
├── frontend/
│   └── (standard Vite + React + TS app)
├── data/
│   └── futon_manufacturing.db   # or .sql seed file
└── README.md
```

---

## Database Requirements

You are given excellent SQL Server schema and data in the `futon-manufacturing/` folder:

- `01-schema.sql`
- `02-sample-data.sql`
- `05-sales-schema-enhancements.sql`
- `06-sales-sample-data.sql`
- `03-manufacturing-reports.sql` + `07-sales-reports.sql`

### Your Tasks:
1. Convert the full schema to clean, modern SQLite.
2. Create a single consolidated seed file: `data/futon_manufacturing_sqlite.sql`
3. Port the most important reports (prioritize top 12 manufacturing + top 10 sales reports).
4. Add new tables for agents:
   - `AgentConversation`
   - `AgentAction`
   - `AgentRecommendation`
   - `AgentAuditLog`

Key domain features that must work:
- Multi-level Bill of Materials (recursive)
- Inventory with full transaction history across warehouses
- Production orders + material issuance + completions
- Purchase orders
- Multi-channel sales (Retail, Online, Wholesale) + quotes + returns
- Work centers and capacity
- Quality inspections

---

## AI Agents (This is the most important part)

Build **at least these 6 agents** using LangGraph:

1. **MRP & Material Planning Agent**  
   Full BOM explosion, net requirements, shortage detection, recommended purchase orders and production timing.

2. **Production Scheduler Agent**  
   Capacity-aware scheduling, bottleneck detection, feasible schedule proposals.

3. **Inventory Intelligence Agent**  
   ABC analysis, dynamic reorder points, slow/dead stock detection, disposition recommendations.

4. **Sales & Pricing Agent**  
   Margin-protected quoting, channel pricing, cross-sell suggestions, discount optimization.

5. **Quality & Process Agent**  
   Defect pattern analysis by supplier, material, work center. Root cause hypotheses + corrective actions.

6. **Demand Forecasting + Executive Agent**  
   Statistical forecasting + LLM narrative. Natural language interface to the entire system.

### Agent Rules (Strict)
- Use proper LangGraph state machines.
- Agents can **only propose actions** — never write to the database directly.
- Every proposal must be reviewable and require explicit human approval.
- All agent reasoning, tool calls, and decisions must be fully logged.
- Provide a clean "Agent Action Approval" workflow in both API and UI.

---

## Required Frontend Pages

1. **Executive Dashboard**  
   KPIs, charts, and "Recommended Actions" panel fed by agents.

2. **Items & BOM Explorer**  
   Powerful list + interactive React Flow BOM tree with cost roll-ups.

3. **Inventory Operations**  
   Multi-warehouse view, transactions, shortage alerts, one-click actions.

4. **Production Command Center**  
   Live work orders, capacity visualization, material availability checks.

5. **Sales Operations**  
   Multi-channel pipeline, quotes, returns, rep performance.

6. **AI Agents Hub** (Star Feature)  
   - Beautiful agent cards with "Run" buttons  
   - Unified chat interface  
   - Clear approval queue for proposed actions  
   - Full reasoning traces  
   - "Ask anything" natural language bar

7. **Reports**  
   Manufacturing + Sales reports with filters and CSV export.

---

## Implementation Priorities

**Phase 1 (Core MVP)**
- SQLite schema + full sample data loaded
- FastAPI with core entities + BOM explosion + key reports
- Basic React app with Dashboard, Items, Inventory, Production
- 2 working agents (MRP + Inventory) with full propose → approve → execute flow

**Phase 2**
- All 6 agents + supervisor
- Interactive BOM visualizer
- Sales flows + full report suite
- Polished manufacturing-grade UI

---

## Quality Requirements

- End-to-end strong typing
- Clean separation: routers → services → agents
- Excellent error handling and validation
- Idempotent, safe seed script
- Outstanding README with exact commands to run everything locally
- Environment-variable driven LLM configuration (no hard-coded keys)

---

## Final Success Criteria

After generation, a developer should be able to:
1. Run one command/file to get a fully populated manufacturing SQLite database
2. Start the backend
3. Start the frontend
4. Immediately use the AI agents on real data and approve actions that actually update the database

---

## Reference Data

All original SQL files are located in the `futon-manufacturing/` directory next to this prompt.

Use them as the single source of truth for the data model, sample data realism, and report semantics.

---

**Now build the complete system.**

Focus on making the AI agents feel powerful, trustworthy, and deeply integrated with the manufacturing domain. The quality of the agent experience will determine whether this feels like a normal app or a genuinely intelligent manufacturing operating system.

Start building.
