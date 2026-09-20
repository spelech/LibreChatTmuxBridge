"""
Tmux Driver implementation for asynchronous subprocess management.
"""

import asyncio
import logging
import shlex
from typing import Protocol

from librechat_tmux_bridge.config import BridgeConfig, settings
from librechat_tmux_bridge.core.exceptions import (
    CommandExecutionError,
    SessionAlreadyExistsError,
    SessionNotFoundError,
)
from librechat_tmux_bridge.core.models import CommandResult, TmuxSession

logger = logging.getLogger(__name__)


class ITmuxDriver(Protocol):
    """Abstract interface protocol for tmux operations to ensure testability."""

    async def list_sessions(self) -> list[TmuxSession]:
        """List all active tmux sessions."""
        ...

    async def has_session(self, session: str) -> bool:
        """Check if a tmux session exists."""
        ...

    async def new_session(
        self, session: str, start_dir: str | None = None, command: str | None = None
    ) -> TmuxSession:
        """Create a new detached tmux session."""
        ...

    async def kill_session(self, session: str) -> bool:
        """Kill an existing tmux session."""
        ...

    async def capture_pane(self, session: str, lines: int = 200, ansi: bool = False) -> str:
        """Capture terminal scrollback buffer from the active pane."""
        ...

    async def send_keys(self, session: str, keys: str, enter: bool = True) -> bool:
        """Send keystrokes or input text to a session pane."""
        ...

    async def run_command(self, args: list[str]) -> CommandResult:
        """Execute an arbitrary tmux command."""
        ...


class TmuxDriver:
    """Subprocess-based tmux driver interacting with host /usr/bin/tmux."""

    def __init__(self, config: BridgeConfig | None = None):
        self.config = config or settings

    def _build_cmd(self, args: list[str]) -> list[str]:
        """Construct command arguments prepending custom socket if configured."""
        cmd = [self.config.tmux_bin]
        if self.config.tmux_socket:
            cmd.extend(["-S", self.config.tmux_socket])
        cmd.extend(args)
        return cmd

    async def run_command(self, args: list[str]) -> CommandResult:
        """Execute a tmux command asynchronously and return exit code and streams."""
        full_cmd = self._build_cmd(args)
        cmd_str = " ".join(shlex.quote(c) for c in full_cmd)

        try:
            proc = await asyncio.create_subprocess_exec(
                *full_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            stdout_str = stdout.decode("utf-8", errors="replace")
            stderr_str = stderr.decode("utf-8", errors="replace")
            exit_code = proc.returncode if proc.returncode is not None else -1

            return CommandResult(
                command=cmd_str,
                stdout=stdout_str,
                stderr=stderr_str,
                exit_code=exit_code,
                success=(exit_code == 0),
            )
        except Exception as ex:
            logger.error(f"Failed to execute tmux command: {cmd_str} - {ex}")
            return CommandResult(
                command=cmd_str,
                stdout="",
                stderr=str(ex),
                exit_code=-1,
                success=False,
            )

    async def list_sessions(self) -> list[TmuxSession]:
        """Retrieve list of active sessions with window counts and status."""
        # Format: session_name|session_windows|session_created|session_attached|window_name
        fmt = "#{session_name}|#{session_windows}|#{session_created}|#{session_attached}|#{window_name}"
        res = await self.run_command(["list-sessions", "-F", fmt])

        if not res.success:
            # When no tmux server is running, tmux returns exit code 1 with "no server running"
            if (
                "no server running" in res.stderr.lower()
                or "error connecting to" in res.stderr.lower()
            ):
                return []
            if "no sessions" in res.stderr.lower():
                return []
            logger.warning(f"tmux list-sessions returned error: {res.stderr.strip()}")
            return []

        sessions: list[TmuxSession] = []
        for line in res.stdout.strip().splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split("|")
            if len(parts) >= 5:
                name, windows_str, created_str, attached_str, win_name = parts[:5]
                try:
                    windows = int(windows_str)
                except ValueError:
                    windows = 1
                try:
                    created = int(created_str)
                except ValueError:
                    created = None
                attached = attached_str == "1"
                sessions.append(
                    TmuxSession(
                        name=name,
                        windows=windows,
                        created=created,
                        attached=attached,
                        active_window=win_name or None,
                    )
                )
            elif len(parts) >= 1 and parts[0]:
                sessions.append(TmuxSession(name=parts[0]))

        return sessions

    async def has_session(self, session: str) -> bool:
        """Check if target session exists."""
        res = await self.run_command(["has-session", "-t", session])
        return res.success

    async def new_session(
        self, session: str, start_dir: str | None = None, command: str | None = None
    ) -> TmuxSession:
        """Spawn a new detached tmux session."""
        if await self.has_session(session):
            raise SessionAlreadyExistsError(session)

        args = ["new-session", "-d", "-s", session]
        if start_dir:
            args.extend(["-c", start_dir])
        if command:
            args.append(command)

        res = await self.run_command(args)
        if not res.success:
            raise CommandExecutionError(" ".join(args), res.exit_code, res.stderr)

        return TmuxSession(name=session, windows=1, attached=False)

    async def kill_session(self, session: str) -> bool:
        """Terminate a tmux session."""
        if not await self.has_session(session):
            raise SessionNotFoundError(session)

        res = await self.run_command(["kill-session", "-t", session])
        if not res.success:
            raise CommandExecutionError(f"kill-session -t {session}", res.exit_code, res.stderr)
        return True

    async def capture_pane(self, session: str, lines: int = 200, ansi: bool = False) -> str:
        """Capture terminal buffer history up to lines."""
        if not await self.has_session(session):
            raise SessionNotFoundError(session)

        args = ["capture-pane", "-pt", session, "-S", f"-{lines}"]
        if ansi:
            args.append("-e")

        res = await self.run_command(args)
        if not res.success:
            raise CommandExecutionError(f"capture-pane -t {session}", res.exit_code, res.stderr)

        return res.stdout

    async def send_keys(self, session: str, keys: str, enter: bool = True) -> bool:
        """Send keys to target session."""
        if not await self.has_session(session):
            raise SessionNotFoundError(session)

        args = ["send-keys", "-t", session, keys]
        if enter:
            args.append("Enter")

        res = await self.run_command(args)
        if not res.success:
            raise CommandExecutionError(f"send-keys -t {session}", res.exit_code, res.stderr)
        return True
