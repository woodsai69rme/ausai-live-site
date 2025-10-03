"""
FastAPI Backend for Archon Knowledge Engine

This is the main entry point for the Archon backend API.
It uses a modular approach with separate API modules for different functionality.

Modules:
- settings_api: Settings and credentials management
- mcp_api: MCP server management and WebSocket streaming
- knowledge_api: Knowledge base, crawling, and RAG operations
- projects_api: Project and task management with streaming
"""

import asyncio
import logging
import os
import uuid
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .api_routes.agent_chat_api import router as agent_chat_router
from .api_routes.agent_routes import router as agent_router
from .api_routes.bug_report_api import router as bug_report_router
from .api_routes.coverage_api import router as coverage_router
from .api_routes.internal_api import router as internal_router
from .api_routes.knowledge_api import router as knowledge_router
from .api_routes.mcp_api import router as mcp_router
from .api_routes.projects_api import router as projects_router

# Phase 2-4: Real Money Implementation Routes
from .api_routes.payment_routes import router as payment_router
from .api_routes.trading_routes import router as trading_router
from .api_routes.live_trading_routes import router as live_trading_router
from .api_routes.ai_trading_routes import router as ai_trading_router

# PRODUCTION Revenue-Generating Endpoints
from .api_routes.revenue_ai_coding_routes import router as revenue_ai_coding_router
from .api_routes.revenue_crypto_signals_routes import router as revenue_crypto_signals_router
from .api_routes.revenue_consulting_routes import router as revenue_consulting_router
from .api_routes.revenue_payment_routes import router as revenue_payment_router

# Multi-AI Routing System
from .api_routes.multi_ai_routes import router as multi_ai_router

# Unlimited OpenRouter Access System
from .api_routes.unlimited_openrouter_routes import router as unlimited_openrouter_router

# OpenRouter Models Management System
from .api_routes.openrouter_models_api import router as openrouter_models_router, startup_event as openrouter_startup

# Claudable Integration System
from .api_routes.claudable_routes import router as claudable_router

# Claude Code Integration System
from .api_routes.claude_code_routes import router as claude_code_router

# Import Socket.IO handlers to ensure they're registered
from .api_routes import socketio_handlers  # This registers all Socket.IO event handlers

# Import modular API routers
from .api_routes.settings_api import router as settings_router
from .api_routes.tests_api import router as tests_router
# from .api_routes.specifications_api import router as specifications_router  # Temporarily disabled
from .api_routes.ai_coding_api import router as ai_coding_router
from .api_routes.agent_orchestration_api import router as agent_orchestration_router
from .api_routes.dashboard_api import router as dashboard_router

# Defensive Security & Ethical Hacking Platform
from .api_routes.defensive_security_routes import router as defensive_security_router

# Security Training Platform
from .api_routes.security_training_api import router as security_training_router
from .api_routes.advanced_osint_api import router as advanced_osint_router
from .api_routes.bug_bounty_automation_api import router as bug_bounty_automation_router

# Threat Intelligence Correlation System
from .api_routes.threat_correlation_api import router as threat_correlation_router
# Security Training Simulation System
from .api_routes.security_training_api import router as security_training_router
# Advanced Threat Hunting System
from .api_routes.threat_hunting_api import router as threat_hunting_router

# Import Logfire configuration
from .config.logfire_config import api_logger, setup_logfire
from .services.background_task_manager import cleanup_task_manager
from .services.crawler_manager import cleanup_crawler, initialize_crawler

# Import enhanced dependencies and optimizations
from .dependencies import setup_service_container, cleanup_service_container
from .exceptions import (
    archon_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
    ArchonException
)
from .utils.performance import get_performance_tracker, performance_report
from .services.circuit_breaker import get_all_circuit_breaker_stats

# Import utilities and core classes
from .services.credential_service import initialize_credentials

# Import Socket.IO integration
from .socketio_app import create_socketio_app

# Import missing dependencies that the modular APIs need
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig
except ImportError:
    # These are optional dependencies for full functionality
    AsyncWebCrawler = None
    BrowserConfig = None

# Logger will be initialized after credentials are loaded
logger = logging.getLogger(__name__)

# Set up logging configuration to reduce noise

# Override uvicorn's access log format to be less verbose
uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.setLevel(logging.WARNING)  # Only log warnings and errors, not every request

# CrawlingContext has been replaced by CrawlerManager in services/crawler_manager.py

# Global flag to track if initialization is complete
_initialization_complete = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks."""
    global _initialization_complete
    _initialization_complete = False

    # Startup
    logger.info("🚀 Starting Archon backend...")

    try:
        # Initialize credentials from database FIRST - this is the foundation for everything else
        await initialize_credentials()

        # Now that credentials are loaded, we can properly initialize logging
        # This must happen AFTER credentials so LOGFIRE_ENABLED is set from database
        setup_logfire(service_name="archon-backend")

        # Initialize enhanced service container
        await setup_service_container()
        api_logger.info("✅ Service container initialized")

        # Now we can safely use the logger
        logger.info("✅ Credentials initialized")
        api_logger.info("🔥 Logfire initialized for backend")

        # Initialize crawling context
        try:
            await initialize_crawler()
        except Exception as e:
            api_logger.warning(f"Could not fully initialize crawling context: {str(e)}")

        # Make crawling context available to modules
        # Crawler is now managed by CrawlerManager

        # Initialize Socket.IO services
        try:
            # Import API modules to register their Socket.IO handlers
            api_logger.info("✅ Socket.IO handlers imported from API modules")
        except Exception as e:
            api_logger.warning(f"Could not initialize Socket.IO services: {e}")

        # Initialize prompt service
        try:
            from .services.prompt_service import prompt_service

            await prompt_service.load_prompts()
            api_logger.info("✅ Prompt service initialized")
        except Exception as e:
            api_logger.warning(f"Could not initialize prompt service: {e}")

        # Set the main event loop for background tasks
        try:
            from .services.background_task_manager import get_task_manager

            task_manager = get_task_manager()
            current_loop = asyncio.get_running_loop()
            task_manager.set_main_loop(current_loop)
            api_logger.info("✅ Main event loop set for background tasks")
        except Exception as e:
            api_logger.warning(f"Could not set main event loop: {e}")

        # MCP Client functionality removed from architecture
        # Agents now use MCP tools directly

        # Initialize OpenRouter model service
        try:
            await openrouter_startup()
            api_logger.info("✅ OpenRouter model service initialized")
        except Exception as e:
            api_logger.warning(f"OpenRouter model service initialization failed: {e}")

        # Initialize Agent Orchestration Service
        try:
            from .services.agent_orchestration_service import agent_orchestration_service
            await agent_orchestration_service.initialize()
            api_logger.info("✅ Agent Orchestration Service initialized")
        except Exception as e:
            api_logger.warning(f"Agent Orchestration Service initialization failed: {e}")

        # Mark initialization as complete
        _initialization_complete = True
        api_logger.info("🎉 Archon backend started successfully!")

    except Exception as e:
        api_logger.error(f"❌ Failed to start backend: {str(e)}")
        raise

    yield

    # Shutdown
    _initialization_complete = False
    api_logger.info("🛑 Shutting down Archon backend...")

    try:
        # MCP Client cleanup not needed

        # Cleanup crawling context
        try:
            await cleanup_crawler()
        except Exception as e:
            api_logger.warning("Could not cleanup crawling context", error=str(e))

        # Cleanup background task manager
        try:
            await cleanup_task_manager()
            api_logger.info("Background task manager cleaned up")
        except Exception as e:
            api_logger.warning("Could not cleanup background task manager", error=str(e))

        # Cleanup service container
        try:
            await cleanup_service_container()
            api_logger.info("Service container cleaned up")
        except Exception as e:
            api_logger.warning("Could not cleanup service container", error=str(e))

        api_logger.info("✅ Cleanup completed")

    except Exception as e:
        api_logger.error(f"❌ Error during shutdown: {str(e)}")


# Create FastAPI application with enhanced configuration
app = FastAPI(
    title="Archon Knowledge Engine API",
    description="Backend API for the Archon knowledge management and project automation platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ARCHON_ENV") == "development" else None,
    redoc_url="/redoc" if os.getenv("ARCHON_ENV") == "development" else None,
)

# Add enhanced exception handlers
app.add_exception_handler(ArchonException, archon_exception_handler)
app.add_exception_handler(ValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# SECURITY: Configure CORS with restricted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3737",    # Frontend development
        "http://localhost:3000",    # Alt frontend port
        "https://yourdomain.com",   # Production domain
        "https://archon.yourdomain.com"  # Production subdomain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Specific methods only
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],  # Specific headers
)


# Enhanced middleware with performance monitoring and request tracking
@app.middleware("http")
async def enhanced_middleware(request: Request, call_next):
    # Generate request ID for tracing
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Start performance tracking
    start_time = time.time()

    # Skip detailed logging for health check endpoints
    is_health_check = request.url.path in ["/health", "/api/health"]

    if is_health_check:
        # Temporarily suppress the log
        import logging
        logger = logging.getLogger("uvicorn.access")
        old_level = logger.level
        logger.setLevel(logging.ERROR)

    try:
        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Add performance headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{duration:.3f}s"

        # Log slow requests (but not health checks)
        if not is_health_check and duration > 1.0:  # Log requests > 1 second
            api_logger.warning(
                f"Slow request detected",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "duration": duration,
                    "status_code": response.status_code
                }
            )

        return response

    except Exception as e:
        duration = time.time() - start_time
        api_logger.error(
            f"Request failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "duration": duration,
                "error": str(e)
            }
        )
        raise

    finally:
        if is_health_check:
            # Restore original log level
            logger.setLevel(old_level)


# Include API routers
app.include_router(settings_router)
app.include_router(mcp_router)
# app.include_router(mcp_client_router)  # Removed - not part of new architecture
app.include_router(knowledge_router)
app.include_router(projects_router)
app.include_router(tests_router)
# app.include_router(specifications_router)  # Spec-Driven Development Integration - Temporarily disabled
app.include_router(ai_coding_router)  # AI Coding Enhancement Integration
app.include_router(agent_orchestration_router)  # Agent Orchestration System
app.include_router(dashboard_router)  # Ultimate Dashboard Integration
app.include_router(agent_chat_router)
app.include_router(agent_router)  # Complete AI Agent Integration System

# Multi-AI Routing System
app.include_router(multi_ai_router)  # Intelligent AI model routing and selection

# Unlimited OpenRouter Access System
app.include_router(unlimited_openrouter_router)  # Unlimited OpenRouter access with rate limit bypass

# OpenRouter Models Management
app.include_router(openrouter_models_router)  # Auto-updating free models management

# Claudable Integration System
app.include_router(claudable_router)  # AI-powered web app generation and management

# Claude Code Integration System
app.include_router(claude_code_router)  # Advanced Claude Code features and workflows

# Phase 2-4: Real Money Implementation API Routes
app.include_router(payment_router)      # Phase 2: Real payment processing
app.include_router(trading_router)      # Phase 3: Live market data feeds
app.include_router(live_trading_router) # Phase 4: Live order execution
app.include_router(ai_trading_router)   # Phase 4: AI trading automation

# PRODUCTION Revenue-Generating API Routes
app.include_router(revenue_ai_coding_router)       # $0.50 per AI coding request
app.include_router(revenue_crypto_signals_router)  # Crypto signals subscriptions ($29.99-$99.99/month)
app.include_router(revenue_consulting_router)      # Consulting sessions ($150-$250/session)
app.include_router(revenue_payment_router)         # Enhanced payment processing with revenue tracking
app.include_router(internal_router)
app.include_router(coverage_router)
app.include_router(bug_report_router)

# Defensive Security & Ethical Hacking Platform
app.include_router(defensive_security_router)  # Anti-scammer protection & bug bounty integration

# Security Training Platform
app.include_router(security_training_router)  # Interactive security training and simulations
app.include_router(advanced_osint_router)      # Advanced OSINT automation framework
app.include_router(bug_bounty_automation_router)  # Advanced bug bounty automation system

# Threat Intelligence Correlation System
app.include_router(threat_correlation_router)  # Real-time threat intelligence correlation and analysis
# Advanced Threat Hunting System
app.include_router(threat_hunting_router)       # Proactive threat hunting and behavioral analysis


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "Archon Knowledge Engine API",
        "version": "1.0.0",
        "description": "Backend API for knowledge management and project automation",
        "status": "healthy",
        "modules": ["settings", "mcp", "mcp-clients", "knowledge", "projects"],
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint that indicates true readiness including credential loading."""
    from datetime import datetime

    # Check if initialization is complete
    if not _initialization_complete:
        return {
            "status": "initializing",
            "service": "archon-backend",
            "timestamp": datetime.now().isoformat(),
            "message": "Backend is starting up, credentials loading...",
            "ready": False,
        }

    return {
        "status": "healthy",
        "service": "archon-backend",
        "timestamp": datetime.now().isoformat(),
        "ready": True,
        "credentials_loaded": True,
    }


# API health check endpoint (alias for /health at /api/health)
@app.get("/api/health")
async def api_health_check():
    """API health check endpoint - alias for /health."""
    return await health_check()


# Performance monitoring endpoints (development only)
@app.get("/api/performance/stats")
async def performance_stats():
    """Get performance statistics (development only)."""
    if os.getenv("ARCHON_ENV") != "development":
        return {"error": "Performance stats only available in development mode"}

    return performance_report()


@app.get("/api/performance/circuit-breakers")
async def circuit_breaker_stats():
    """Get circuit breaker statistics (development only)."""
    if os.getenv("ARCHON_ENV") != "development":
        return {"error": "Circuit breaker stats only available in development mode"}

    return get_all_circuit_breaker_stats()


# Create Socket.IO app wrapper
# This wraps the FastAPI app with Socket.IO functionality
socket_app = create_socketio_app(app)

# Export the socket_app for uvicorn to use
# The socket_app still handles all FastAPI routes, but also adds Socket.IO support


def main():
    """Main entry point for running the server."""
    import uvicorn

    # Require ARCHON_SERVER_PORT to be set
    server_port = os.getenv("ARCHON_SERVER_PORT")
    if not server_port:
        raise ValueError(
            "ARCHON_SERVER_PORT environment variable is required. "
            "Please set it in your .env file or environment. "
            "Default value: 8181"
        )

    uvicorn.run(
        "src.server.main:socket_app",
        host="0.0.0.0",
        port=int(server_port),
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()
