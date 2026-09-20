"""
Diagnostic tap points, ring buffers, and 6-part agent feedback envelope generator.
"""

import json
import time
from collections import deque
from typing import Any

from librechat_tmux_bridge.config import settings


class DiagnosticTap:
    """In-memory diagnostic ring buffer for inspecting runtime state during test harnesses."""

    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.events: deque[dict[str, Any]] = deque(maxlen=capacity)
        self.request_count = 0
        self.error_count = 0
        self.start_time = time.time()

    def record_event(self, event_type: str, payload: dict[str, Any]) -> None:
        """Add an event to the ring buffer."""
        record = {
            "timestamp": time.time(),
            "event_type": event_type,
            **payload,
        }
        self.events.append(record)
        if event_type == "request":
            self.request_count += 1
        elif event_type == "error":
            self.error_count += 1

    def get_recent_events(self, limit: int = 20) -> list[dict[str, Any]]:
        """Retrieve recent events from buffer."""
        return list(self.events)[-limit:]

    def clear(self) -> None:
        """Flush ring buffer."""
        self.events.clear()
        self.request_count = 0
        self.error_count = 0

    def stats(self) -> dict[str, Any]:
        """Summary statistics."""
        return {
            "uptime_seconds": time.time() - self.start_time,
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "buffer_depth": len(self.events),
        }


# Global tap point singleton
diagnostic_tap = DiagnosticTap()


def format_agent_feedback_envelope(
    test_name: str,
    inputs: dict[str, Any],
    assumptions: list[str],
    active_settings: dict[str, Any] | None,
    action_history: list[dict[str, Any]],
    output_delta: dict[str, Any],
    captured_logs: list[str],
    reproduction_command: str,
) -> str:
    """
    Format a standardized 6-part agent feedback envelope according to
    AgenticEngineeringToolbelt testing harness standards.
    """
    envelope = {
        "status": "FAILED",
        "test_name": test_name,
        "inputs": inputs,
        "assumptions": assumptions,
        "active_settings": active_settings
        or {
            "host": settings.host,
            "port": settings.port,
            "poll_interval_sec": settings.poll_interval_sec,
            "quiescence_timeout_sec": settings.quiescence_timeout_sec,
        },
        "action_history": action_history,
        "output_delta": output_delta,
        "captured_logs": captured_logs,
        "reproduction_command": reproduction_command,
    }
    return json.dumps(envelope, indent=2)
