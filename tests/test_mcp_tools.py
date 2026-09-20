"""
Unit tests for Model Context Protocol (MCP) server tools.
"""

import json
from unittest.mock import AsyncMock, patch

import pytest

from librechat_tmux_bridge.core.models import CommandResult, TmuxSession
from librechat_tmux_bridge.mcp.server import (
    capture_tmux_pane_tool,
    create_tmux_session_tool,
    execute_tmux_command_tool,
    kill_tmux_session_tool,
    list_tmux_sessions_tool,
    send_tmux_keys_tool,
    tmux_quick_approve_prompt,
    tmux_status_summary_prompt,
    tmux_supervise_agent_prompt,
)


@pytest.mark.asyncio
async def test_mcp_list_sessions():
    with patch(
        "librechat_tmux_bridge.mcp.server.driver.list_sessions",
        new=AsyncMock(
            return_value=[
                TmuxSession(
                    name="test1", windows=1, created=1700000000, attached=True, active_window="bash"
                )
            ]
        ),
    ):
        result_json = await list_tmux_sessions_tool()
        data = json.loads(result_json)
        assert data["status"] == "ok"
        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["name"] == "test1"

    with patch(
        "librechat_tmux_bridge.mcp.server.driver.list_sessions", new=AsyncMock(return_value=[])
    ):
        result_empty = await list_tmux_sessions_tool()
        data_empty = json.loads(result_empty)
        assert data_empty["status"] == "empty"


@pytest.mark.asyncio
async def test_mcp_capture_pane():
    with patch(
        "librechat_tmux_bridge.mcp.server.driver.capture_pane",
        new=AsyncMock(return_value="\x1b[32mHello World\x1b[0m"),
    ):
        out_clean = await capture_tmux_pane_tool("test1", lines=50, strip_escape_codes=True)
        assert out_clean == "Hello World"

        out_raw = await capture_tmux_pane_tool("test1", lines=50, strip_escape_codes=False)
        assert "\x1b[32m" in out_raw

    with patch(
        "librechat_tmux_bridge.mcp.server.driver.capture_pane",
        new=AsyncMock(side_effect=Exception("Session missing")),
    ):
        out_err = await capture_tmux_pane_tool("missing", lines=50)
        assert "Error capturing pane" in out_err


@pytest.mark.asyncio
async def test_mcp_send_keys():
    with patch(
        "librechat_tmux_bridge.mcp.server.driver.send_keys", new=AsyncMock(return_value=True)
    ):
        res = await send_tmux_keys_tool("test1", "git status", enter=True)
        assert "Successfully sent keystrokes" in res

    with patch(
        "librechat_tmux_bridge.mcp.server.driver.send_keys",
        new=AsyncMock(side_effect=Exception("Failed")),
    ):
        res_err = await send_tmux_keys_tool("missing", "git status")
        assert "Error sending keys" in res_err


@pytest.mark.asyncio
async def test_mcp_create_and_kill_session():
    with patch(
        "librechat_tmux_bridge.mcp.server.driver.new_session",
        new=AsyncMock(return_value=TmuxSession(name="agent-tui")),
    ):
        res = await create_tmux_session_tool("agent-tui", start_dir="/containers", command="agy")
        assert "Session 'agent-tui' created successfully" in res
        assert "Directory: /containers" in res

    with patch(
        "librechat_tmux_bridge.mcp.server.driver.new_session",
        new=AsyncMock(side_effect=Exception("Already exists")),
    ):
        res_err = await create_tmux_session_tool("agent-tui")
        assert "Error creating session" in res_err

    with patch(
        "librechat_tmux_bridge.mcp.server.driver.kill_session", new=AsyncMock(return_value=True)
    ):
        res_kill = await kill_tmux_session_tool("agent-tui")
        assert "Session 'agent-tui' killed successfully" in res_kill

    with patch(
        "librechat_tmux_bridge.mcp.server.driver.kill_session",
        new=AsyncMock(side_effect=Exception("Not found")),
    ):
        res_kill_err = await kill_tmux_session_tool("missing")
        assert "Error killing session" in res_kill_err


@pytest.mark.asyncio
async def test_mcp_execute_tmux_command():
    with patch(
        "librechat_tmux_bridge.mcp.server.driver.run_command",
        new=AsyncMock(
            return_value=CommandResult(
                command="list-windows -t infra",
                stdout="0: bash* (1 panes)",
                stderr="",
                exit_code=0,
                success=True,
            )
        ),
    ):
        res = await execute_tmux_command_tool("list-windows -t infra")
        data = json.loads(res)
        assert data["success"] is True
        assert "bash" in data["stdout"]

    with patch(
        "librechat_tmux_bridge.mcp.server.driver.run_command",
        new=AsyncMock(side_effect=Exception("Bad command")),
    ):
        res_err = await execute_tmux_command_tool("bad-cmd")
        assert "Error executing tmux command" in res_err


def test_mcp_prompts():
    # 1. Supervise prompt
    prompt_supervise = tmux_supervise_agent_prompt("agy-work", task_goal="Refactor auth module")
    assert "agy-work" in prompt_supervise
    assert "Refactor auth module" in prompt_supervise
    assert "capture_tmux_pane" in prompt_supervise
    assert "send_tmux_keys" in prompt_supervise

    # 2. Quick approve prompt
    prompt_approve = tmux_quick_approve_prompt("infra")
    assert "infra" in prompt_approve
    assert "keys='y'" in prompt_approve

    # 3. Status summary prompt
    prompt_status = tmux_status_summary_prompt()
    assert "list_tmux_sessions" in prompt_status
    assert "capture_tmux_pane" in prompt_status
