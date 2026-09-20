"""
Controls Simulation & Disturbance Harness for LibreChatTmuxBridge.
Executes high-volume multi-turn loops, disturbance injection, and emits 6-part feedback envelope on failure.
"""

import time

import pytest

from librechat_tmux_bridge.config import BridgeConfig
from librechat_tmux_bridge.core.terminal_streamer import TerminalStreamer
from librechat_tmux_bridge.infrastructure.taps import format_agent_feedback_envelope
from tests.conftest import MockTmuxDriver


@pytest.mark.asyncio
async def test_high_volume_simulation_harness():
    """High-volume closed-loop simulation executing 50 multi-turn requests with disturbances."""
    driver = MockTmuxDriver()
    config = BridgeConfig(
        poll_interval_sec=0.005,
        quiescence_timeout_sec=0.02,
        stream_timeout_sec=1.0,
    )
    streamer = TerminalStreamer(driver, config)

    batch_size = 50
    actions_taken: list[dict] = []
    captured_logs: list[str] = []
    start_ts = time.time()

    disturbances = [
        ("infra", "normal command 1"),
        ("infra", ""),  # empty payload
        ("non_existent", "command to missing session"),  # missing session disturbance
        ("infra", "/keys C-c"),  # special key interruption
        ("infra", "/list"),  # slash command
        ("infra", "a" * 500),  # large buffer payload
        ("infra", "/new sim-worker /tmp 'python3'"),  # dynamic session spawn
        ("sim-worker", "import math; print(math.pi)"),  # execution on newly spawned session
        ("sim-worker", "/kill sim-worker"),  # clean teardown
    ]

    try:
        for i in range(batch_size):
            session, cmd = disturbances[i % len(disturbances)]
            step_action = {"step": i + 1, "session": session, "cmd": cmd[:30], "status": "PENDING"}

            chunks = []
            async for chunk_line in streamer.stream_command(session, cmd):
                chunks.append(chunk_line)

            assert len(chunks) >= 1, f"Step {i}: expected at least one SSE chunk"
            assert chunks[-1] == "data: [DONE]\n\n", f"Step {i}: stream did not end with [DONE]"

            step_action["status"] = "OK"
            step_action["chunks_count"] = len(chunks)
            actions_taken.append(step_action)

        elapsed = time.time() - start_ts
        throughput = batch_size / elapsed
        captured_logs.append(
            f"Processed {batch_size} turns in {elapsed:.2f}s ({throughput:.1f} turns/sec)"
        )

        assert throughput >= 5.0, f"Throughput {throughput:.1f} turns/sec below 5.0 threshold"

    except Exception as ex:
        envelope = format_agent_feedback_envelope(
            test_name="test_high_volume_simulation_harness",
            inputs={"batch_size": batch_size, "disturbances_count": len(disturbances)},
            assumptions=[
                "MockTmuxDriver correctly maintains in-memory buffers",
                "SSE stream cleanly terminates with [DONE]",
            ],
            active_settings={
                "poll_interval_sec": config.poll_interval_sec,
                "quiescence_timeout_sec": config.quiescence_timeout_sec,
            },
            action_history=actions_taken[-10:],
            output_delta={"error": str(ex)},
            captured_logs=captured_logs,
            reproduction_command="uv run pytest tests/test_simulation_harness.py",
        )
        print("\n--- AGENT FEEDBACK ENVELOPE ---")
        print(envelope)
        raise
