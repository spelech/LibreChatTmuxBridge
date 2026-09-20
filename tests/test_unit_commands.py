"""
Unit tests for slash command parsing and execution across all bridge commands.
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
    assert "/approve" in res_help
    assert "/tail" in res_help

    # 2. /list (populated & empty)
    res_list = await streamer.handle_slash_command("list", [])
    assert "agy-work" in res_list
    assert "infra" in res_list

    mock_driver.sessions.clear()
    res_empty_list = await streamer.handle_slash_command("list", [])
    assert "No active tmux sessions found" in res_empty_list

    # Restore sessions
    mock_driver.__init__()

    # 3. /status
    res_status = await streamer.handle_slash_command("status", [])
    assert "LibreChatTmuxBridge Status" in res_status
    assert "Active Sessions" in res_status

    # 4. /y or /approve
    res_app_ok = await streamer.handle_slash_command("approve", [], session_name="infra")
    assert "Approved" in res_app_ok
    assert ("infra", "y", True) in mock_driver.command_history

    res_app_arg = await streamer.handle_slash_command("y", ["agy-work"])
    assert "Approved" in res_app_arg
    assert ("agy-work", "y", True) in mock_driver.command_history

    res_app_err = await streamer.handle_slash_command("approve", [])
    assert "No active session specified" in res_app_err

    res_app_fail = await streamer.handle_slash_command("approve", [], session_name="missing")
    assert "Failed to send approval" in res_app_fail

    # 5. /n or /reject
    res_rej_ok = await streamer.handle_slash_command("reject", [], session_name="infra")
    assert "Rejected" in res_rej_ok
    assert ("infra", "n", True) in mock_driver.command_history

    res_rej_err = await streamer.handle_slash_command("no", [])
    assert "No active session specified" in res_rej_err

    res_rej_fail = await streamer.handle_slash_command("reject", [], session_name="missing")
    assert "Failed to send rejection" in res_rej_fail

    # 6. /c or /cancel
    res_can_ok = await streamer.handle_slash_command("cancel", [], session_name="infra")
    assert "SIGINT" in res_can_ok
    assert ("infra", "C-c", False) in mock_driver.command_history

    res_can_err = await streamer.handle_slash_command("sigint", [])
    assert "No active session specified" in res_can_err

    res_can_fail = await streamer.handle_slash_command("cancel", [], session_name="missing")
    assert "Failed to send SIGINT" in res_can_fail

    # 7. /enter
    res_enter = await streamer.handle_slash_command("enter", [], session_name="infra")
    assert "Sent **Enter**" in res_enter
    assert ("infra", "Enter", False) in mock_driver.command_history

    res_enter_fail = await streamer.handle_slash_command("enter", [], session_name="missing")
    assert "Failed to send Enter" in res_enter_fail

    # 8. /esc
    res_esc = await streamer.handle_slash_command("esc", [], session_name="infra")
    assert "Sent **Escape**" in res_esc
    assert ("infra", "Escape", False) in mock_driver.command_history

    res_esc_fail = await streamer.handle_slash_command("esc", [], session_name="missing")
    assert "Failed to send Escape" in res_esc_fail

    # 9. /eof
    res_eof = await streamer.handle_slash_command("eof", [], session_name="infra")
    assert "Sent **EOF**" in res_eof
    assert ("infra", "C-d", False) in mock_driver.command_history

    res_eof_fail = await streamer.handle_slash_command("eof", [], session_name="missing")
    assert "Failed to send EOF" in res_eof_fail

    # 10. /up & /down
    res_up = await streamer.handle_slash_command("up", [], session_name="infra")
    assert "Repeated previous command" in res_up
    assert ("infra", "Up", True) in mock_driver.command_history

    res_up_fail = await streamer.handle_slash_command("up", [], session_name="missing")
    assert "Failed to send Up arrow" in res_up_fail

    res_down = await streamer.handle_slash_command("down", [], session_name="infra")
    assert "Sent Down arrow" in res_down
    assert ("infra", "Down", False) in mock_driver.command_history

    res_down_fail = await streamer.handle_slash_command("down", [], session_name="missing")
    assert "Failed to send Down arrow" in res_down_fail

    # 11. /clear
    res_clear = await streamer.handle_slash_command("clear", [], session_name="infra")
    assert "Cleared terminal buffer" in res_clear
    assert ("infra", "clear", True) in mock_driver.command_history

    res_clear_fail = await streamer.handle_slash_command("clear", [], session_name="missing")
    assert "Failed to clear" in res_clear_fail

    # 12. /tail
    res_tail_default = await streamer.handle_slash_command("tail", [], session_name="infra")
    assert "Last 25 lines of `infra`" in res_tail_default

    res_tail_count = await streamer.handle_slash_command("tail", ["10"], session_name="infra")
    assert "Last 10 lines of `infra`" in res_tail_count

    res_tail_target = await streamer.handle_slash_command("tail", ["agy-work", "15"])
    assert "Last 15 lines of `agy-work`" in res_tail_target

    res_tail_target_nan = await streamer.handle_slash_command("tail", ["agy-work", "notanumber"])
    assert "Last 25 lines of `agy-work`" in res_tail_target_nan

    res_tail_fail = await streamer.handle_slash_command("tail", [], session_name="missing")
    assert "Failed to capture tail" in res_tail_fail

    # 13. /peek
    res_peek_usage = await streamer.handle_slash_command("peek", [])
    assert "Usage: `/peek" in res_peek_usage

    res_peek_ok = await streamer.handle_slash_command("peek", ["agy-work", "20"])
    assert "Peek at `agy-work`" in res_peek_ok

    res_peek_nan = await streamer.handle_slash_command("peek", ["agy-work", "nan"])
    assert "Peek at `agy-work`" in res_peek_nan

    res_peek_err = await streamer.handle_slash_command("peek", ["missing-session"])
    assert "Failed to peek" in res_peek_err

    # 14. /new (bare shell, presets, custom command)
    res_new_default = await streamer.handle_slash_command("new", [])
    assert "created successfully" in res_new_default
    assert "Bare interactive shell" in res_new_default

    res_new_bare = await streamer.handle_slash_command("new", ["dev-bare", "/tmp"])
    assert "created successfully" in res_new_bare
    assert "Bare interactive shell" in res_new_bare
    assert await mock_driver.has_session("dev-bare")

    res_new_preset_agy = await streamer.handle_slash_command(
        "new", ["dev-agy", "/containers", "agy"]
    )
    assert "agy --dangerously-skip-permissions" in res_new_preset_agy
    assert await mock_driver.has_session("dev-agy")

    res_new_preset_oc = await streamer.handle_slash_command(
        "new", ["dev-oc", "/containers", "opencode"]
    )
    assert "opencode --dangerously-skip-permissions" in res_new_preset_oc
    assert await mock_driver.has_session("dev-oc")

    res_new_preset_none = await streamer.handle_slash_command("new", ["dev-none", "/tmp", "none"])
    assert "Bare interactive shell" in res_new_preset_none

    res_new_custom = await streamer.handle_slash_command("new", ["dev-test", "/tmp", "python"])
    assert "created successfully" in res_new_custom
    assert await mock_driver.has_session("dev-test")

    res_new_dup = await streamer.handle_slash_command("new", ["dev-test"])
    assert "Failed to create" in res_new_dup

    # 15. /agy command
    res_agy_default = await streamer.handle_slash_command("agy", [])
    assert "Antigravity Agent" in res_agy_default
    assert "--dangerously-skip-permissions" in res_agy_default

    res_agy_named = await streamer.handle_slash_command(
        "agy", ["agy-feature", "/containers", "--mode", "plan"]
    )
    assert "agy-feature" in res_agy_named
    assert "--dangerously-skip-permissions --mode plan" in res_agy_named
    assert await mock_driver.has_session("agy-feature")

    res_agy_dup = await streamer.handle_slash_command("agy", ["agy-feature"])
    assert "Failed to spawn agy" in res_agy_dup

    # 16. /opencode command
    res_oc_default = await streamer.handle_slash_command("opencode", [])
    assert "OpenCode" in res_oc_default
    assert "--dangerously-skip-permissions" in res_oc_default

    res_oc_named = await streamer.handle_slash_command(
        "opencode", ["oc-feature", "/containers", "--auto"]
    )
    assert "oc-feature" in res_oc_named
    assert "--dangerously-skip-permissions --auto" in res_oc_named
    assert await mock_driver.has_session("oc-feature")

    res_oc_dup = await streamer.handle_slash_command("opencode", ["oc-feature"])
    assert "Failed to spawn opencode" in res_oc_dup

    # 17. /kill
    res_kill_fail = await streamer.handle_slash_command("kill", [])
    assert "Usage: `/kill" in res_kill_fail

    res_kill_ok = await streamer.handle_slash_command("kill", ["dev-test"])
    assert "killed" in res_kill_ok
    assert not await mock_driver.has_session("dev-test")

    res_kill_missing = await streamer.handle_slash_command("kill", ["non-existent"])
    assert "Failed to kill" in res_kill_missing

    # 16. /keys
    res_keys_usage = await streamer.handle_slash_command("keys", [])
    assert "Usage: `/keys" in res_keys_usage

    res_keys_no_target = await streamer.handle_slash_command("keys", ["Tab"])
    assert "No active session specified" in res_keys_no_target

    res_keys_ok = await streamer.handle_slash_command("keys", ["Tab"], session_name="infra")
    assert "Sent key `Tab` to session `infra`" in res_keys_ok

    res_keys_with_target = await streamer.handle_slash_command("keys", ["C-c", "agy-work"])
    assert "Sent key `C-c` to session `agy-work`" in res_keys_with_target

    res_keys_fail = await streamer.handle_slash_command("keys", ["C-c"], session_name="missing")
    assert "Failed to send key `C-c` to `missing`" in res_keys_fail

    # 17. Unknown command
    res_unknown = await streamer.handle_slash_command("invalidcmd", [])
    assert "Unknown slash command" in res_unknown


@pytest.mark.asyncio
async def test_stream_slash_command_flow(mock_driver: MockTmuxDriver, test_config):
    streamer = TerminalStreamer(mock_driver, test_config)

    # Streaming /list command
    chunks_list = [c async for c in streamer.stream_command("infra", "/list")]
    assert len(chunks_list) == 2
    assert "Active Host Tmux Sessions" in chunks_list[0]
    assert chunks_list[1] == "data: [DONE]\n\n"

    # Streaming /approve command
    chunks_app = [c async for c in streamer.stream_command("infra", "/approve")]
    assert len(chunks_app) == 2
    assert "Approved" in chunks_app[0]
    assert chunks_app[1] == "data: [DONE]\n\n"

    # Streaming /tail command
    chunks_tail = [c async for c in streamer.stream_command("infra", "/tail 10")]
    assert len(chunks_tail) == 2
    assert "Last 10 lines" in chunks_tail[0]
    assert chunks_tail[1] == "data: [DONE]\n\n"

    # Streaming /keys command
    chunks_keys = [c async for c in streamer.stream_command("infra", "/keys C-c")]
    assert len(chunks_keys) == 2
    assert "Sent key `C-c` to session `infra`" in chunks_keys[0]
    assert chunks_keys[1] == "data: [DONE]\n\n"

    # Non-streaming slash command execution
    result_text = await streamer.execute_command_non_streaming("infra", "/status")
    assert "LibreChatTmuxBridge Status" in result_text
