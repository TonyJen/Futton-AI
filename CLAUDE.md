# Project Notes

## Environment

- OS: Windows-first workflow
- Repository root: `D:\Projects\Funton-Ai`
- Backend runtime: Python 3.11+ in the root virtual environment at `.\.venv`
- Frontend runtime: Node.js 18+
- Backend URL: `http://localhost:8000`
- Frontend URL: `http://localhost:5173`
- Database: SQLite
- AI Supervisor requires API keys in `backend/.env`
- Docker stack: `docker-compose.yml` with `backend/Dockerfile` and `frontend/Dockerfile`

## Usage

### Recommended startup

```powershell
.\start.ps1
```

This script:

- uses the root `.venv`
- installs missing backend/frontend dependencies
- seeds the database if needed
- starts the FastAPI backend in a separate PowerShell window
- starts the Vite frontend in the current window

### Docker startup

```powershell
docker compose up --build
```

- Backend is exposed on `http://localhost:8000`
- Frontend is exposed on `http://localhost:5173`
- Frontend traffic to `/api/*` is proxied to the backend container by Nginx
- The backend container uses `backend/data/futon_manufacturing.db` and seeds that path automatically when it is missing

To pass real AI provider keys into Compose, use:

```powershell
docker compose --env-file backend/.env up --build
```

### Manual startup

#### Backend

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python data\seed.py
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Current Status

- Backend lint passes: `.\.venv\Scripts\python.exe -m ruff check backend --no-cache`
- Backend tests pass: `.\.venv\Scripts\python.exe -m pytest backend -q`
- Frontend lint passes: `cd frontend && npm run lint`
- Frontend build passes: `cd frontend && npm run build`
- Frontend tests pass: `cd frontend && npm run test -- --run`

## Testing

- Repo-root backend tests: `.\.venv\Scripts\python.exe -m pytest backend -q`
- Backend package tests from `backend\`: `python -m pytest tests -q`
- Standalone backend agent tests from `backend\`: `python -m pytest test_agent.py -q`
- Frontend tests: `cd frontend && npm run test -- --run`

## Lint Setup

### Backend

- Linter: Ruff
- Config: `ruff.toml`
- Dependency: `backend/requirements.txt`
- Cache directory is ignored via `.gitignore`

### Frontend

- Linter: ESLint
- Config: `frontend/.eslintrc.cjs`
- TypeScript ESLint packages were aligned with the current TypeScript version

## Coding Style / Conventions

### General

- Prefer Windows-style paths in commands and documentation.
- Keep changes surgical and aligned with the existing structure.
- Reuse existing services, helpers, and schemas instead of duplicating logic.

### Backend

- FastAPI routers live under `backend/app/api/routers`.
- Business logic should stay in services under `backend/app/services`.
- SQLAlchemy 2.0 models are in `backend/app/db/models.py`; prefer real mapped attributes over string-based loader paths.
- Preserve intended `HTTPException` status codes instead of wrapping them into generic 500 responses.
- Test async code with `pytest-asyncio` fixtures and `httpx.ASGITransport`.

### Frontend

- TypeScript runs in `strict` mode.
- Path alias `@/*` maps to `frontend/src/*`.
- Prefer typed API helpers and explicit response types over loose objects.
- Shared UI primitives should use direct prop type aliases instead of empty wrapper interfaces.

## Recent Notes

- Backend lint cleanup included import sorting, unused-variable cleanup, import placement fixes, a truthy SQLAlchemy filter fix, and removal of stale `__all__` exports.
- Frontend lint cleanup included fixing a mutable `mockData` binding, removing an unused callback parameter in `Quotes.tsx`, and replacing empty wrapper interfaces in shared UI components with type aliases.

## Known Non-Blocking Warnings

- Pydantic v2 `Config` deprecation warnings in backend schemas
- One `datetime.utcnow()` deprecation warning in the agents router
- Vite/Vitest plugin deprecation warnings during frontend test runs
