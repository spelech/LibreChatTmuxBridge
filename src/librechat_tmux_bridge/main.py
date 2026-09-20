"""
Main FastAPI application and lifecycle configuration for LibreChatTmuxBridge.
"""

import logging
import shutil
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from librechat_tmux_bridge import __version__
from librechat_tmux_bridge.api.routes_openai import router as openai_router
from librechat_tmux_bridge.api.routes_system import router as system_router
from librechat_tmux_bridge.config import settings
from librechat_tmux_bridge.mcp.server import mcp_server

# Setup structured logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("LibreChatTmuxBridge")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    tmux_path = shutil.which(settings.tmux_bin)
    if not tmux_path:
        logger.warning(
            f"⚠️ Tmux binary '{settings.tmux_bin}' was not found in PATH! "
            "Please ensure tmux is installed."
        )
    else:
        logger.info(f"✅ Discovered tmux binary at: {tmux_path}")

    logger.info(
        f"🚀 LibreChatTmuxBridge v{__version__} listening on http://{settings.host}:{settings.port}"
    )
    logger.info("📡 OpenAI endpoint available at: /v1/models and /v1/chat/completions")
    if settings.mcp_enabled:
        logger.info("🔌 Model Context Protocol (MCP) server available at: /mcp/sse")

    yield

    logger.info("🛑 LibreChatTmuxBridge shutting down cleanly.")


def create_app() -> FastAPI:
    """Application factory."""
    app = FastAPI(
        title="LibreChatTmuxBridge",
        description=(
            "Universal bidirectional bridge between LibreChat and host tmux sessions "
            "for zero-token terminal driving and agentic copilot interaction."
        ),
        version=__version__,
        lifespan=lifespan,
    )

    # Enable CORS for LibreChat PWA and local webapps
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Mount routes
    app.include_router(system_router)
    app.include_router(openai_router)

    # Mount MCP SSE application
    if settings.mcp_enabled:
        try:
            from mcp.server.transport_security import TransportSecuritySettings

            transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)
            sse_app = mcp_server.sse_app(transport_security=transport_security)
        except (TypeError, ImportError):
            sse_app = mcp_server.sse_app()
        app.mount("/mcp", sse_app)

    return app


app = create_app()
