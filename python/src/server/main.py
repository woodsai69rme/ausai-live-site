"""
FastAPI Backend for Archon Knowledge Engine

Minimal working version - only includes existing routes.
Wraps the FastAPI app with Socket.IO via socketio.ASGIApp so /socket.io/*
traffic is handled by python-socketio while the rest falls through to FastAPI.
The Dockerfile CMD runs `uvicorn src.server.main:socket_app --host 0.0.0.0`,
so a module-level `socket_app` is the symbol uvicorn must load.
"""

import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# Note: socketio_handlers is registered transitively via
# `projects_api.py`'s `from .socketio_handlers import ...` import. No
# explicit side-effect import is needed here.
from .api_routes.agent_chat_api import router as agent_chat_router
from .api_routes.auth_api import router as auth_router
from .api_routes.bug_report_api import router as bug_report_router
from .api_routes.coverage_api import router as coverage_router
from .api_routes.dashboard_api import router as dashboard_router
from .api_routes.internal_api import router as internal_router
from .api_routes.knowledge_api import router as knowledge_router
from .api_routes.mcp_api import router as mcp_router
from .api_routes.projects_api import router as projects_router
from .api_routes.settings_api import router as settings_router
from .api_routes.system_api import router as system_router
from .api_routes.tests_api import router as tests_router
from .middleware.security_headers import SecurityHeadersMiddleware
from .socketio_app import create_socketio_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def _parse_cors_origins(raw: str, default: str) -> list[str]:
    """Parse a comma-separated origins env var, defending against empty strings.

    `os.getenv("CORS_ORIGINS", default)` returns "" when the var is set but
    blank, and `"".split(",")` resolves to `[""]` -- a single invalid origin
    that breaks every CORS request. We strip whitespace and drop empties.
    """
    raw = raw if raw else default
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


# Resolve CORS origins once at import. Defaults are conservative but useful
# for local development; production deployments must set CORS_ORIGINS to the
# real origin list. Note: SOCKETIO_CORS_ORIGINS is read separately inside
# `socketio_app.py` (at module-load time) so we do not duplicate it here.
_cors_default = "http://localhost:3737,http://127.0.0.1:3737"
allowed_origins = _parse_cors_origins(os.getenv("CORS_ORIGINS", _cors_default), _cors_default)


@asynccontextmanager
async def lifespan(_app: FastAPI):  # noqa: ARG001
    """Application startup/shutdown -- logs resolved CORS configuration."""
    logger.info("Archon server starting | http_cors=%s", allowed_origins)
    try:
        yield
    finally:
        logger.info("Archon server shutting down")


# Create FastAPI app
app = FastAPI(
    title="Archon Knowledge Engine API",
    description="API for the Archon knowledge management system with MCP integration",
    version="0.1.0",
    lifespan=lifespan,
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Archon Knowledge Engine API",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "archon-api",
        "timestamp": time.time(),
    }


# Include available routers.
# IMPORTANT: `system_router` registers the GET /api/projects/list alias and
# MUST be registered before `projects_router` -- FastAPI matches in insertion
# order, and `/api/projects/{project_id}` would otherwise eat the `list`
# path segment as a project id and silently 404. The same trap applies to
# any future endpoint wanting a stable path under /api/projects/<literal>,
# because projects_api.py also owns these catchalls:
#   /api/projects/{project_id}
#   /api/projects/{project_id}/features
#   /api/projects/{project_id}/docs
#   /api/projects/{project_id}/tasks
#   /api/projects/{project_id}/versions
# If you add /api/projects/dashboard or similar, route it through
# system_router (registered here) -- never after projects_router.
app.include_router(agent_chat_router)
app.include_router(auth_router)
app.include_router(bug_report_router)
app.include_router(coverage_router)
app.include_router(dashboard_router)
app.include_router(internal_router)
app.include_router(knowledge_router)
app.include_router(mcp_router)
app.include_router(system_router)
app.include_router(projects_router)
app.include_router(settings_router)
app.include_router(tests_router)


# Error handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(_request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Per CLAUDE.md (alpha fail-fast): always log the full traceback; expose
    # a generic 500 to clients. FastAPI still returns a structured response
    # rather than crashing the worker, which is what we want for a HTTP
    # boundary -- the failure detail is preserved in observability logs.
    logger.error(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Wrap the FastAPI app with Socket.IO. uvicorn must load `socket_app`
# (matches the CMD in python/Dockerfile.server). The wrapper handles
# `/socket.io/*` traffic and falls through to FastAPI for everything else.
socket_app = create_socketio_app(app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.server.main:socket_app",
        host="0.0.0.0",
        port=int(os.getenv("ARCHON_SERVER_PORT", "8181")),
        workers=1,
    )
