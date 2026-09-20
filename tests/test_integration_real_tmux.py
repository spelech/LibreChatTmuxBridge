"""
Live integration test interacting directly with host /usr/bin/tmux.
"""

import shutil
import uuid

import pytest

from librechat_tmux_bridge.config import BridgeConfig
from librechat_tmux_bridge.core.terminal_streamer import TerminalStreamer
from librechat_tmux_bridge.core.tmux_driver import TmuxDriver


@pytest.mark.asyncio
async def test_real_tmux_lifecycle_and_streaming():
    """Verify end-to-end integration against the real host tmux process."""
    if not shutil.which("tmux"):
        pytest.skip("Host does not have tmux installed in PATH")

    test_sess_id = f"test-int-{uuid.uuid4().hex[:8]}"
    config = BridgeConfig(
        poll_interval_sec=0.05,
        quiescence_timeout_sec=0.3,
        stream_timeout_sec=3.0,
    )
    driver = TmuxDriver(config)
    streamer = TerminalStreamer(driver, config)

    try:
        # 1. Create session
        created = await driver.new_session(test_sess_id, command="bash")
        assert created.name == test_sess_id
        assert await driver.has_session(test_sess_id)

        # 2. Check in list_sessions
        all_sessions = await driver.list_sessions()
        session_names = [s.name for s in all_sessions]
        assert test_sess_id in session_names

        # 3. Stream a real command
        chunks = []
        async for chunk in streamer.stream_command(test_sess_id, "echo 'REAL_TMUX_INTEGRATION_OK'"):
            chunks.append(chunk)

        combined_text = "".join(chunks)
        assert "REAL_TMUX_INTEGRATION_OK" in combined_text
        assert "data: [DONE]\n\n" in combined_text

    finally:
        # 4. Clean up session
        if await driver.has_session(test_sess_id):
            await driver.kill_session(test_sess_id)
            assert not await driver.has_session(test_sess_id)
