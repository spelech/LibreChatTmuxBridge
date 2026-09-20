"""
System and health monitoring endpoints.
"""

import time

from fastapi import APIRouter, Depends

from librechat_tmux_bridge import __version__
from librechat_tmux_bridge.config import settings
from librechat_tmux_bridge.core.models import HealthResponse
from librechat_tmux_bridge.core.tmux_driver import ITmuxDriver, TmuxDriver
from librechat_tmux_bridge.infrastructure.taps import diagnostic_tap

router = APIRouter(tags=["System"])

SERVER_START_TIME = time.time()


def get_driver() -> ITmuxDriver:
    return TmuxDriver(settings)


@router.get("/health", response_model=HealthResponse)
async def health_check(driver: ITmuxDriver = Depends(get_driver)) -> HealthResponse:
    """Standard unauthenticated health probe for orchestrators and monitoring."""
    sessions = await driver.list_sessions()
    uptime = time.time() - SERVER_START_TIME
    return HealthResponse(
        status="healthy",
        version=__version__,
        uptime_seconds=round(uptime, 2),
        active_sessions=len(sessions),
    )


@router.get("/api/status")
async def system_status(driver: ITmuxDriver = Depends(get_driver)) -> dict:
    """Detailed operational status including diagnostic tap counters and active sessions."""
    sessions = await driver.list_sessions()
    return {
        "service": "librechat-tmux-bridge",
        "version": __version__,
        "uptime_seconds": round(time.time() - SERVER_START_TIME, 2),
        "settings": {
            "host": settings.host,
            "port": settings.port,
            "tmux_bin": settings.tmux_bin,
            "tmux_socket": settings.tmux_socket,
            "poll_interval_sec": settings.poll_interval_sec,
            "quiescence_timeout_sec": settings.quiescence_timeout_sec,
        },
        "sessions": [s.model_dump() for s in sessions],
        "diagnostics": diagnostic_tap.stats(),
    }
