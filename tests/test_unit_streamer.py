"""
Unit tests for TerminalStreamer: ANSI cleaning, delta differ, and SSE chunk generation.
"""

import pytest

from librechat_tmux_bridge.core.terminal_streamer import (
    TerminalStreamer,
    clean_terminal_output,
    strip_ansi,
)
from tests.conftest import MockTmuxDriver


def test_strip_ansi_and_clean_output():
    raw_vt100 = "\x1b[31;1mERROR:\x1b[0m Failed\x1b[2K\r\nLine 2\r\n\r\n"
    stripped = strip_ansi(raw_vt100)
    assert "\x1b" not in stripped
    assert "ERROR: Failed" in stripped

    cleaned = clean_terminal_output(raw_vt100)
    assert cleaned == "ERROR: Failed\nLine 2"


def test_calculate_delta(test_streamer: TerminalStreamer):
    # Case 1: Empty baseline
    delta1 = test_streamer.calculate_delta("", "line 1\nline 2")
    assert delta1 == "line 1\nline 2"

    # Case 2: Append lines
    base = "line 1\nline 2"
    curr = "line 1\nline 2\nline 3\nline 4"
    delta2 = test_streamer.calculate_delta(base, curr)
    assert delta2 == "line 3\nline 4"

    # Case 3: Sliding window scrollback (overlapping suffix/prefix)
    base_scroll = "line 1\nline 2\nline 3\nline 4"
    curr_scroll = "line 3\nline 4\nline 5\nline 6"
    delta3 = test_streamer.calculate_delta(base_scroll, curr_scroll)
    assert delta3 == "line 5\nline 6"

    # Case 4: Complete screen redraw / clear
    base_redrawn = "old content line A\nold content line B"
    curr_redrawn = "CLEAR SCREEN\nnew brand new content"
    delta4 = test_streamer.calculate_delta(base_redrawn, curr_redrawn)
    assert delta4 == "CLEAR SCREEN\nnew brand new content"


@pytest.mark.asyncio
async def test_stream_command_lifecycle(mock_driver: MockTmuxDriver, test_config):
    streamer = TerminalStreamer(mock_driver, test_config)

    # 1. Non-existent session
    chunks = [c async for c in streamer.stream_command("non_existent_sess", "hello")]
    assert len(chunks) == 2
    assert "❌ Tmux session `non_existent_sess` does not exist" in chunks[0]
    assert chunks[1] == "data: [DONE]\n\n"

    # 2. Existing session command execution
    chunks = [c async for c in streamer.stream_command("infra", "uptime")]
    assert len(chunks) >= 2
    assert any("executed uptime successfully" in c for c in chunks)
    assert chunks[-1] == "data: [DONE]\n\n"

    # 3. Non-streaming execution
    full_output = await streamer.execute_command_non_streaming("infra", "whoami")
    assert "executed whoami successfully" in full_output
