"""
Unit tests for the TmuxDriver implementation and command construction.
"""

from unittest.mock import AsyncMock, patch

import pytest

from librechat_tmux_bridge.config import BridgeConfig
from librechat_tmux_bridge.core.exceptions import (
    CommandExecutionError,
    SessionAlreadyExistsError,
    SessionNotFoundError,
)
from librechat_tmux_bridge.core.models import CommandResult
from librechat_tmux_bridge.core.tmux_driver import TmuxDriver


@pytest.mark.asyncio
async def test_driver_build_cmd():
    cfg_no_socket = BridgeConfig(tmux_bin="/usr/bin/tmux", tmux_socket=None)
    driver1 = TmuxDriver(cfg_no_socket)
    cmd1 = driver1._build_cmd(["list-sessions"])
    assert cmd1 == ["/usr/bin/tmux", "list-sessions"]

    cfg_socket = BridgeConfig(tmux_bin="tmux", tmux_socket="/tmp/custom.sock")
    driver2 = TmuxDriver(cfg_socket)
    cmd2 = driver2._build_cmd(["list-sessions"])
    assert cmd2 == ["tmux", "-S", "/tmp/custom.sock", "list-sessions"]


@pytest.mark.asyncio
async def test_driver_list_sessions_parsing():
    driver = TmuxDriver()

    # Case 1: Standard 5-part format
    mock_stdout = "sess1|2|1700000000|1|bash\nsess2|1|1700000100|0|vim\n"
    with patch.object(
        driver,
        "run_command",
        new=AsyncMock(
            return_value=CommandResult(
                command="test", stdout=mock_stdout, stderr="", exit_code=0, success=True
            )
        ),
    ):
        sessions = await driver.list_sessions()
        assert len(sessions) == 2
        assert sessions[0].name == "sess1"
        assert sessions[0].windows == 2
        assert sessions[0].attached is True
        assert sessions[0].active_window == "bash"
        assert sessions[1].name == "sess2"
        assert sessions[1].windows == 1
        assert sessions[1].attached is False
        assert sessions[1].active_window == "vim"

    # Case 2: Server not running
    with patch.object(
        driver,
        "run_command",
        new=AsyncMock(
            return_value=CommandResult(
                command="test",
                stdout="",
                stderr="error connecting to /tmp/tmux-1000/default (no server running)",
                exit_code=1,
                success=False,
            )
        ),
    ):
        assert await driver.list_sessions() == []

    # Case 3: No sessions
    with patch.object(
        driver,
        "run_command",
        new=AsyncMock(
            return_value=CommandResult(
                command="test", stdout="", stderr="no sessions", exit_code=1, success=False
            )
        ),
    ):
        assert await driver.list_sessions() == []

    # Case 4: Fallback 1-part format
    with patch.object(
        driver,
        "run_command",
        new=AsyncMock(
            return_value=CommandResult(
                command="test", stdout="single_session\n", stderr="", exit_code=0, success=True
            )
        ),
    ):
        sessions = await driver.list_sessions()
        assert len(sessions) == 1
        assert sessions[0].name == "single_session"


@pytest.mark.asyncio
async def test_driver_new_session_lifecycle():
    driver = TmuxDriver()

    with patch.object(driver, "has_session", new=AsyncMock(return_value=True)):
        with pytest.raises(SessionAlreadyExistsError):
            await driver.new_session("existing_sess")

    with patch.object(driver, "has_session", new=AsyncMock(return_value=False)):
        with patch.object(
            driver,
            "run_command",
            new=AsyncMock(
                return_value=CommandResult(
                    command="test", stdout="", stderr="", exit_code=0, success=True
                )
            ),
        ):
            sess = await driver.new_session("new_sess", start_dir="/containers", command="bash")
            assert sess.name == "new_sess"

        # Failure case
        with patch.object(
            driver,
            "run_command",
            new=AsyncMock(
                return_value=CommandResult(
                    command="test", stdout="", stderr="failed to create", exit_code=1, success=False
                )
            ),
        ):
            with pytest.raises(CommandExecutionError):
                await driver.new_session("fail_sess")


@pytest.mark.asyncio
async def test_driver_kill_and_capture_errors():
    driver = TmuxDriver()

    with patch.object(driver, "has_session", new=AsyncMock(return_value=False)):
        with pytest.raises(SessionNotFoundError):
            await driver.kill_session("non_existent")

        with pytest.raises(SessionNotFoundError):
            await driver.capture_pane("non_existent")

        with pytest.raises(SessionNotFoundError):
            await driver.send_keys("non_existent", "test")

    with patch.object(driver, "has_session", new=AsyncMock(return_value=True)):
        with patch.object(
            driver,
            "run_command",
            new=AsyncMock(
                return_value=CommandResult(
                    command="test", stdout="", stderr="kill error", exit_code=1, success=False
                )
            ),
        ):
            with pytest.raises(CommandExecutionError):
                await driver.kill_session("target")

        with patch.object(
            driver,
            "run_command",
            new=AsyncMock(
                return_value=CommandResult(
                    command="test", stdout="captured line", stderr="", exit_code=0, success=True
                )
            ),
        ):
            out = await driver.capture_pane("target", lines=50, ansi=True)
            assert out == "captured line"


@pytest.mark.asyncio
async def test_driver_run_command_exception():
    driver = TmuxDriver(BridgeConfig(tmux_bin="/non/existent/path/to/tmux"))
    res = await driver.run_command(["list-sessions"])
    assert res.success is False
    assert res.exit_code == -1
