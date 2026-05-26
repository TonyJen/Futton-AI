# Futon Manufacturing ERP — Backend (FastAPI)

**Wave 2 FastAPI Backend Builder — Phase 1 Complete**

High-quality, clean-architecture FastAPI backend for the Futon Manufacturing ERP. Fully ready for the AI Agents wave.

## Tech Stack (Phase 1)

- **FastAPI** + **SQLAlchemy 2.0** (async + aiosqlite)
- **Pydantic v2** schemas
- **SQLite** (via consolidated `data/futon_manufacturing_sqlite.sql`)
- Alembic for migrations
- Clean layered architecture: `routers → services → models`

## Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app + lifespan + routers
│   ├── core/
│   │   ├── config.py           # Pydantic Settings
│   │   └── deps.py             # DB + auth dependencies
│   ├── db/
│   │   ├── session.py          # Async + sync engines
│   │   └── models.py           # SQLAlchemy 2.0 models (full schema match)
│   ├── schemas/                # Pydantic v2 models (request/response)
│   ├── api/routers/            # All API endpoints
│   ├── services/               # Business logic (BOM explosion, inventory, etc.)
│   └── agents/                 # LangGraph-ready stubs + MRP example
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── ...
├── alembic.ini
├── requirements.txt
└── README.md
```

## Key Phase 1 Features Delivered

- **Models**: Items, BillOfMaterials, Inventory, ProductionOrder, SalesOrder + all supporting tables + Agent tables
- **Working recursive BOM explosion** (`GET /api/v1/bom/explosion/{item_id}`) — handles scrap rates and unlimited depth
- Full CRUD + list for Items, Inventory, Production Orders, Sales Orders, BOM entries
- Inventory adjustments & transactions
- Production completion recording + BOM-based material suggestions
- Clean dependency injection and service layer (agents will love this)
- CORS preconfigured for Vite React dev server
- Health endpoints and OpenAPI docs at `/docs`

## Quick Start

### 1. Install dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 2. Prepare the Database (DB Agent output)

The consolidated schema + seed lives at:

```
../data/futon_manufacturing_sqlite.sql
```

Run it against SQLite (example with sqlite3 CLI or any tool):

```powershell
cd ..
sqlite3 data/futon_manufacturing.db < data/futon_manufacturing_sqlite.sql
```

Or use any GUI / Python script. This creates `data/futon_manufacturing.db` with full data.

### 3. Run the backend

```powershell
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit:
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- BOM Explosion example (after seeding): http://localhost:8000/api/v1/bom/explosion/1

## Environment Variables

Create a `.env` file in `backend/` (optional — defaults are sane):

```env
DATABASE_URL=sqlite+aiosqlite:///./data/futon_manufacturing.db
ALEMBIC_DATABASE_URL=sqlite:///./data/futon_manufacturing.db
DEBUG=true
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
```

## Alembic Migrations

```powershell
cd backend

# After changing models
alembic revision --autogenerate -m "your change description"

alembic upgrade head
```

**Note**: The initial schema is delivered via the SQL seed file. Autogenerate works great once the DB exists.

## Important Endpoints (Phase 1)

- `GET /api/v1/items` — list + search
- `GET /api/v1/bom/explosion/{item_id}?quantity=10` — **recursive BOM explosion** (the star)
- `GET /api/v1/inventory` — current stock levels across warehouses
- `POST /api/v1/inventory/adjust` — manual adjustments
- `GET /api/v1/production/orders/{id}` — includes materials
- `POST /api/v1/production/orders/{id}/complete`
- Sales + Customer endpoints also functional

## For AI Agents (Next Wave)

All business logic lives in `app/services/`. Agents should:

1. Inject `AsyncSession`
2. Instantiate `BOMService`, `InventoryService`, etc.
3. Call methods like `bom_service.explode_bom(...)`
4. Use the `propose_action(...)` pattern from `BaseAgent`

Example (already works today):

```python
from app.agents.mrp_agent import MRPPlanningAgent
from app.db.session import AsyncSessionLocal

async with AsyncSessionLocal() as db:
    agent = MRPPlanningAgent(db)
    plan = await agent.run({"item_id": 42, "order_quantity": 50})
```

## Next Steps / Integration

- Wave 2 AI Agents Builder will extend `app/agents/`
- Frontend will consume these endpoints via TanStack Query
- Add auth (JWT) in `core/deps.py` when ready
- Expand reports and MRP netting inside services

---

**Built as part of Wave 2 — File-writing only, zero shell project scaffolding.**

Ready for immediate use once the SQLite seed is applied.
