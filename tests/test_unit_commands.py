"""
Unit tests for slash command parsing and execution (/new, /kill, /list, /keys, /help).
"""

import pytest

from librechat_tmux_bridge.core.terminal_streamer import TerminalStreamer
from tests.conftest import MockTmuxDriver


def test_parse_slash_command(test_streamer: TerminalStreamer):
    assert test_streamer.parse_slash_command("normal text") is None
    assert test_streamer.parse_slash_command("") is None
    assert test_streamer.parse_slash_command("  /list  ") == ("list", [])
    assert test_streamer.parse_slash_command("/new test-sess /containers 'bash -l'") == (
        "new",
        ["test-sess", "/containers", "bash -l"],
    )


@pytest.mark.asyncio
async def test_slash_command_execution(mock_driver: MockTmuxDriver, test_config):
    streamer = TerminalStreamer(mock_driver, test_config)

    # 1. /help
    res_help = await streamer.handle_slash_command("help", [])
    assert "LibreChat Tmux Bridge Commands" in res_help
    assert "/new" in res_help

    # 2. /list
    res_list = await streamer.handle_slash_command("list", [])
    assert "agy-work" in res_list
    assert "infra" in res_list

    # 3. /new
    res_new_fail = await streamer.handle_slash_command("new", [])
    assert "Usage: `/new" in res_new_fail

    res_new_ok = await streamer.handle_slash_command("new", ["dev-test", "/tmp", "python"])
    assert "created successfully" in res_new_ok
    assert await mock_driver.has_session("dev-test")

    # 4. /new duplicate
    res_new_dup = await streamer.handle_slash_command("new", ["dev-test"])
    assert "Failed to create" in res_new_dup

    # 5. /kill
    res_kill_fail = await streamer.handle_slash_command("kill", [])
    assert "Usage: `/kill" in res_kill_fail

    res_kill_ok = await streamer.handle_slash_command("kill", ["dev-test"])
    assert "killed" in res_kill_ok
    assert not await mock_driver.has_session("dev-test")

    # 6. /keys
    res_keys = await streamer.handle_slash_command("keys", ["C-c"])
    assert "Special keys command received" in res_keys

    # 7. Unknown command
    res_unknown = await streamer.handle_slash_command("invalidcmd", [])
    assert "Unknown slash command" in res_unknown


@pytest.mark.asyncio
async def test_stream_slash_command_flow(mock_driver: MockTmuxDriver, test_config):
    streamer = TerminalStreamer(mock_driver, test_config)

    # Streaming /list command
    chunks = [c async for c in streamer.stream_command("infra", "/list")]
    assert len(chunks) == 2
    assert "Active Host Tmux Sessions" in chunks[0]
    assert chunks[1] == "data: [DONE]\n\n"

    # Streaming /keys command
    chunks_keys = [c async for c in streamer.stream_command("infra", "/keys C-c")]
    assert len(chunks_keys) == 2
    assert "Sent key `C-c` to session `infra`" in chunks_keys[0]
    assert chunks_keys[1] == "data: [DONE]\n\n"
