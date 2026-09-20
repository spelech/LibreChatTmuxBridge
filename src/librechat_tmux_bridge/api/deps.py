"""
Dependency providers for FastAPI routers.
"""

from librechat_tmux_bridge.config import settings
from librechat_tmux_bridge.core.terminal_streamer import TerminalStreamer
from librechat_tmux_bridge.core.tmux_driver import ITmuxDriver, TmuxDriver


def get_driver() -> ITmuxDriver:
    """Dependency provider for ITmuxDriver."""
    return TmuxDriver(settings)


def get_streamer() -> TerminalStreamer:
    """Dependency provider for TerminalStreamer."""
    return TerminalStreamer(get_driver(), settings)
