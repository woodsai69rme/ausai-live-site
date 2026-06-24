"""
Socket.IO Server Integration for Archon

Simple Socket.IO server setup with FastAPI integration.
All events are handled in projects_api.py using @sio.event decorators.
"""

import logging
import os

import socketio
from fastapi import FastAPI

from .config.logfire_config import safe_logfire_info

logger = logging.getLogger(__name__)


def _get_cors_origins() -> list[str]:
    origins = []
    development_origins = [
        "http://localhost:3737",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3737",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    production_origins = os.getenv("SOCKETIO_CORS_ORIGINS", "")
    if production_origins:
        origins.extend([origin.strip() for origin in production_origins.split(",") if origin.strip()])
    if os.getenv("ARCHON_ENV") != "production":
        origins.extend(development_origins)
    if not origins:
        origins = development_origins
    return origins


_socketio_cors_origins = _get_cors_origins()

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=_socketio_cors_origins,
    logger=False,
    engineio_logger=False,
    max_http_buffer_size=1000000,
    ping_timeout=300,
    ping_interval=60,
)

# Global Socket.IO instance for use across modules
_socketio_instance: socketio.AsyncServer | None = None


def get_socketio_instance() -> socketio.AsyncServer:
    """Get the global Socket.IO server instance."""
    global _socketio_instance
    if _socketio_instance is None:
        _socketio_instance = sio
    return _socketio_instance


def create_socketio_app(app: FastAPI) -> socketio.ASGIApp:
    """
    Wrap FastAPI app with Socket.IO ASGI app.

    Args:
        app: FastAPI application instance

    Returns:
        Socket.IO ASGI app that wraps the FastAPI app
    """
    safe_logfire_info(
        "Creating Socket.IO server", cors_origins=_socketio_cors_origins, ping_timeout=300, ping_interval=60
    )

    # Note: Socket.IO event handlers are registered in socketio_handlers.py
    # This module only creates the Socket.IO server instance

    # Create and return the Socket.IO ASGI app
    socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

    # Store the app reference for later use
    sio.app = app

    return socket_app
