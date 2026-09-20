"""
Model Context Protocol (MCP) server for LibreChatTmuxBridge.
Exposes tmux orchestration tools to LibreChat agent mode and external MCP clients.
"""

import json
import logging
import shlex

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:
    from mcp.server import MCPServer

from librechat_tmux_bridge import __version__
from librechat_tmux_bridge.config import settings
from librechat_tmux_bridge.core.terminal_streamer import clean_terminal_output
from librechat_tmux_bridge.core.tmux_driver import TmuxDriver

logger = logging.getLogger("LibreChatTmuxBridge.MCP")

mcp_server = MCPServer(
    name="librechat-tmux-bridge",
    instructions=(
        "Universal bidirectional bridge to host terminal multiplexer (tmux). "
        "Allows inspecting, controlling, and managing terminal sessions and persistent "
        "AI agent TUIs (Antigravity 'agy', OpenCode) on the host server."
    ),
    version=__version__,
)

driver = TmuxDriver(settings)


@mcp_server.tool(name="list_tmux_sessions")
async def list_tmux_sessions_tool() -> str:
    """List all active tmux sessions currently running on the host system.

    Returns:
        JSON string containing list of active sessions with window counts and attached status.
    """
    sessions = await driver.list_sessions()
    if not sessions:
        return json.dumps({"status": "empty", "sessions": []})
    return json.dumps(
        {"status": "ok", "sessions": [s.model_dump() for s in sessions]},
        indent=2,
    )


@mcp_server.tool(name="capture_tmux_pane")
async def capture_tmux_pane_tool(
    session_name: str,
    lines: int = 100,
    strip_escape_codes: bool = True,
) -> str:
    """Capture recent terminal output / scrollback buffer from an active tmux session pane.

    Args:
        session_name: Name of target tmux session (e.g. 'agy-work', 'opencode', 'infra').
        lines: Number of history lines to capture from scrollback (default: 100).
        strip_escape_codes: Whether to strip ANSI/VT100 escape codes (default: True).

    Returns:
        Captured text content of the terminal pane.
    """
    try:
        raw_output = await driver.capture_pane(session_name, lines=lines)
        if strip_escape_codes:
            return clean_terminal_output(raw_output)
        return raw_output
    except Exception as ex:
        return f"Error capturing pane for session '{session_name}': {ex}"


@mcp_server.tool(name="send_tmux_keys")
async def send_tmux_keys_tool(
    session_name: str,
    keys: str,
    enter: bool = True,
) -> str:
    """Send text, shell commands, or key sequences to an active tmux session.

    Args:
        session_name: Name of target tmux session.
        keys: Command string or key combination to send (e.g. 'git status', 'C-c', 'y').
        enter: Whether to press Enter after the keys (default: True). Set False for confirmation keys.

    Returns:
        Confirmation of keystroke delivery.
    """
    try:
        await driver.send_keys(session_name, keys, enter=enter)
        return f"Successfully sent keystrokes to session '{session_name}' (enter={enter})."
    except Exception as ex:
        return f"Error sending keys to session '{session_name}': {ex}"


@mcp_server.tool(name="create_tmux_session")
async def create_tmux_session_tool(
    session_name: str,
    start_dir: str | None = None,
    command: str | None = None,
) -> str:
    """Spawn a new detached tmux session on the host.

    Args:
        session_name: Unique name for the new tmux session.
        start_dir: Optional working directory for the session (defaults to current dir).
        command: Optional shell command or process to execute on spawn (e.g. 'agy', 'opencode').

    Returns:
        Status message confirming session initialization.
    """
    try:
        session = await driver.new_session(session_name, start_dir=start_dir, command=command)
        msg = f"Session '{session.name}' created successfully."
        if start_dir:
            msg += f" Directory: {start_dir}."
        if command:
            msg += f" Command: {command}."
        return msg
    except Exception as ex:
        return f"Error creating session '{session_name}': {ex}"


@mcp_server.tool(name="kill_tmux_session")
async def kill_tmux_session_tool(session_name: str) -> str:
    """Terminate and destroy an existing tmux session.

    Args:
        session_name: Name of tmux session to terminate.

    Returns:
        Status message confirming session termination.
    """
    try:
        await driver.kill_session(session_name)
        return f"Session '{session_name}' killed successfully."
    except Exception as ex:
        return f"Error killing session '{session_name}': {ex}"


@mcp_server.tool(name="execute_tmux_command")
async def execute_tmux_command_tool(command_args: str) -> str:
    """Execute a raw tmux CLI subcommand safely on the host.

    Args:
        command_args: Subcommand string (e.g. 'list-windows -t infra' or 'display-message -p "#{pane_current_path}"').

    Returns:
        Command stdout, stderr, and exit status.
    """
    try:
        args = shlex.split(command_args)
        result = await driver.run_command(args)
        return json.dumps(
            {
                "success": result.success,
                "exit_code": result.exit_code,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
            },
            indent=2,
        )
    except Exception as ex:
        return f"Error executing tmux command '{command_args}': {ex}"
