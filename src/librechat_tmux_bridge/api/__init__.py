"""
API routers for OpenAI compatibility and system probes.
"""

from librechat_tmux_bridge.api.routes_openai import router as openai_router
from librechat_tmux_bridge.api.routes_system import router as system_router

__all__ = ["openai_router", "system_router"]
