"""Wild Turkey — FastAPI Application Entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import close_db, init_db
from app.routers import (
    admin,
    approvals_sse,
    auth,
    browser_workflows,
    harvester,
    mcp,
    memory,
    monitors,
    providers,
    reports,
    skills,
    swarm,
    tasks,
    terminal,
    audio,
)

logging.basicConfig(
    level=logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    try:
        await init_db()
    except Exception as e:
        logger.warning(f"Database initialization skipped or failed: {e}")
    yield
    logger.info("Closing database...")
    await close_db()


app = FastAPI(
    title="Wild Turkey",
    version="5.5.0",
    description="Compliant AI resource orchestration dashboard",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "5.5.0", "environment": settings.ENVIRONMENT}


# Include all routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(providers.router, prefix="/api/v1/providers", tags=["providers"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(monitors.router, prefix="/api/v1/monitors", tags=["monitors"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(approvals_sse.router, prefix="/api/v1/approvals", tags=["approvals"])
app.include_router(mcp.router, prefix="/api/v1/mcp", tags=["mcp"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(browser_workflows.router, prefix="/api/v1/browser", tags=["browser"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["memory"])
app.include_router(harvester.router, prefix="/api/v1/harvester", tags=["harvester"])
app.include_router(swarm.router, prefix="/api/v1/swarm", tags=["swarm"])
app.include_router(terminal.router, prefix="/api/v1/terminal", tags=["terminal"])
app.include_router(skills.router, prefix="/api/v1/skills", tags=["skills"])
app.include_router(audio.router, prefix="/api/audio", tags=["audio"])

logger.info(
    "Routers registered: auth, providers, tasks, monitors, admin, approvals_sse, mcp, reports, browser_workflows, memory, harvester, swarm, terminal, skills"
)
