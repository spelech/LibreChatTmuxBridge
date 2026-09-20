"""
Pytest configuration, fixtures, and mock implementations for testing.
"""

import pytest
from fastapi.testclient import TestClient

from librechat_tmux_bridge.api.deps import get_driver, get_streamer
from librechat_tmux_bridge.config import BridgeConfig
from librechat_tmux_bridge.core.exceptions import (
    SessionAlreadyExistsError,
    SessionNotFoundError,
)
from librechat_tmux_bridge.core.models import CommandResult, TmuxSession
from librechat_tmux_bridge.core.terminal_streamer import TerminalStreamer
from librechat_tmux_bridge.main import app


class MockTmuxDriver:
    """Mock in-memory tmux driver for deterministic unit and simulation testing."""

    def __init__(self):
        self.sessions: dict[str, TmuxSession] = {
            "agy-work": TmuxSession(
                name="agy-work", windows=1, created=1700000000, attached=False, active_window="agy"
            ),
            "infra": TmuxSession(
                name="infra", windows=2, created=1700000100, attached=True, active_window="bash"
            ),
        }
        self.pane_buffers: dict[str, str] = {
            "agy-work": "antigravity agent ready\n> ",
            "infra": "root@server:/# ls\nbin etc var\nroot@server:/# ",
        }
        self.command_history: list[tuple[str, str, bool]] = []
        self.fail_next_command = False

    async def list_sessions(self) -> list[TmuxSession]:
        return list(self.sessions.values())

    async def has_session(self, session: str) -> bool:
        return session in self.sessions

    async def new_session(
        self, session: str, start_dir: str | None = None, command: str | None = None
    ) -> TmuxSession:
        if session in self.sessions:
            raise SessionAlreadyExistsError(session)
        s = TmuxSession(
            name=session, windows=1, created=1700000200, attached=False, active_window="bash"
        )
        self.sessions[session] = s
        self.pane_buffers[session] = (
            f"Initialized in {start_dir or '/'} with {command or 'bash'}\n$ "
        )
        return s

    async def kill_session(self, session: str) -> bool:
        if session not in self.sessions:
            raise SessionNotFoundError(session)
        del self.sessions[session]
        if session in self.pane_buffers:
            del self.pane_buffers[session]
        return True

    async def capture_pane(self, session: str, lines: int = 200, ansi: bool = False) -> str:
        if session not in self.sessions:
            raise SessionNotFoundError(session)
        return self.pane_buffers.get(session, "")

    async def send_keys(self, session: str, keys: str, enter: bool = True) -> bool:
        if session not in self.sessions:
            raise SessionNotFoundError(session)
        self.command_history.append((session, keys, enter))

        # Simulate terminal echo and output response
        current = self.pane_buffers.get(session, "")
        simulated_output = f"{keys}\nOutput: executed {keys} successfully\n$ "
        self.pane_buffers[session] = current + simulated_output
        return True

    async def run_command(self, args: list[str]) -> CommandResult:
        if self.fail_next_command:
            self.fail_next_command = False
            return CommandResult(
                command=" ".join(args),
                stdout="",
                stderr="Simulated failure",
                exit_code=1,
                success=False,
            )
        return CommandResult(
            command=" ".join(args), stdout="mock output", stderr="", exit_code=0, success=True
        )


@pytest.fixture
def mock_driver() -> MockTmuxDriver:
    return MockTmuxDriver()


@pytest.fixture
def test_config() -> BridgeConfig:
    return BridgeConfig(
        host="127.0.0.1",
        port=8035,
        poll_interval_sec=0.01,
        quiescence_timeout_sec=0.05,
        stream_timeout_sec=2.0,
    )


@pytest.fixture
def test_streamer(mock_driver: MockTmuxDriver, test_config: BridgeConfig) -> TerminalStreamer:
    return TerminalStreamer(mock_driver, test_config)


@pytest.fixture
def client(mock_driver: MockTmuxDriver, test_streamer: TerminalStreamer) -> TestClient:
    app.dependency_overrides[get_driver] = lambda: mock_driver
    app.dependency_overrides[get_streamer] = lambda: test_streamer
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
