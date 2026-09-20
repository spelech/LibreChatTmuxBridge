"""
Domain exceptions for LibreChatTmuxBridge.
"""


class TmuxBridgeError(Exception):
    """Base domain exception for all bridge errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class SessionNotFoundError(TmuxBridgeError):
    """Raised when an operation targets a non-existent tmux session."""

    def __init__(self, session_name: str):
        super().__init__(f"Tmux session '{session_name}' not found", {"session": session_name})


class SessionAlreadyExistsError(TmuxBridgeError):
    """Raised when attempting to create a session that already exists."""

    def __init__(self, session_name: str):
        super().__init__(f"Tmux session '{session_name}' already exists", {"session": session_name})


class CommandExecutionError(TmuxBridgeError):
    """Raised when a tmux command execution fails."""

    def __init__(self, command: str, exit_code: int, stderr: str):
        super().__init__(
            f"Tmux command failed with exit code {exit_code}: {stderr.strip()}",
            {"command": command, "exit_code": exit_code, "stderr": stderr},
        )


class StreamTimeoutError(TmuxBridgeError):
    """Raised when terminal delta streaming exceeds maximum execution timeout."""

    def __init__(self, session_name: str, timeout_sec: float):
        super().__init__(
            f"Terminal stream on session '{session_name}' exceeded timeout of {timeout_sec}s",
            {"session": session_name, "timeout_sec": timeout_sec},
        )
