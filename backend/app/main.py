"""
Funton AI Manufacturing ERP - Main FastAPI Application (Phase 1)

Wires together:
- Core DB (async SQLAlchemy + aiosqlite)
- All API routers including the star feature: /api/v1/agents
- Lifespan events for startup/shutdown
- CORS for the React frontend

This file + the agents/ package is what makes the AI the most important differentiator.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.db.session import close_db, init_db
# Try to import the agents router from the new location first
try:
    from app.api.routers.agents import router as agents_router
except ImportError:
    try:
        from app.agents.router import router as agents_router
    except ImportError:
        agents_router = None
        import logging
        logging.getLogger("funton.main").warning("AI Agents router not found - AI features disabled")

# Import other routers (Phase 2/3)
try:
    from app.api.routers.items import router as items_router
except ImportError:
    items_router = None

try:
    from app.api.routers.inventory import router as inventory_router
except ImportError:
    inventory_router = None

try:
    from app.api.routers.production import router as production_router
except ImportError:
    production_router = None

try:
    from app.api.routers.sales import router as sales_router
except ImportError:
    sales_router = None

try:
    from app.api.routers.purchasing import router as purchasing_router
except ImportError:
    purchasing_router = None

settings = get_settings()

# Configure logging (excellent observability for agents too)
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("funton.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager."""
    logger.info("=== Starting Funton AI Manufacturing ERP ===")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info(f"Database: {settings.DATABASE_URL}")

    # Optional: auto-create tables in dev (prefer Alembic in real deploys)
    if settings.DEBUG:
        try:
            await init_db()
            logger.info("Database tables ensured (dev mode)")
        except Exception as e:
            logger.warning(f"init_db note: {e}")

    yield

    logger.info("Shutting down...")
    await close_db()
    logger.info("=== Shutdown complete ===")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Futon Manufacturing ERP with LangGraph Agents and Human-in-the-Loop Approval",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS - critical for frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# ROOT & HEALTH
# =============================================================================

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "ai_agents": "Phase 3 - MRP + Inventory agents + full Sales/Quotes/Returns + Purchasing foundation",
        "docs": "/docs",
        "agents_hub": "/api/v1/agents",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "phase": "3 - Purchasing + Sales/CRM + 2 Production Agents (full propose/approve/execute)",
    }


# =============================================================================
# API ROUTERS
# =============================================================================

# Mount the Agents router (the star of the show)
if agents_router is not None:
    app.include_router(agents_router, prefix=settings.API_V1_PREFIX)
else:
    logger.warning("AI Agents router could not be loaded")

# Core operations routers (Phase 2+)
if items_router:
    app.include_router(items_router, prefix=settings.API_V1_PREFIX)
if inventory_router:
    app.include_router(inventory_router, prefix=settings.API_V1_PREFIX)
if production_router:
    app.include_router(production_router, prefix=settings.API_V1_PREFIX)
if sales_router:
    app.include_router(sales_router, prefix=settings.API_V1_PREFIX)
if purchasing_router:
    app.include_router(purchasing_router, prefix=settings.API_V1_PREFIX)

# Update health to reflect progress


# =============================================================================
# GLOBAL EXCEPTION HANDLER (good DX)
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if settings.DEBUG else "Contact support",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
