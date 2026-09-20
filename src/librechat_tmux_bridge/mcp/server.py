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
    preset: str | None = None,
) -> str:
    """Spawn a new detached tmux session on the host.

    Args:
        session_name: Unique name for the new tmux session.
        start_dir: Optional working directory for the session (defaults to current dir).
        command: Optional shell command or process to execute on spawn. Leave empty/None for a bare shell.
        preset: Optional agent launcher preset: 'agy' (launches agy --dangerously-skip-permissions) or 'opencode' (launches opencode --dangerously-skip-permissions).

    Returns:
        Status message confirming session initialization.
    """
    effective_cmd = command
    if preset == "agy" or command in ("agy", "--agy"):
        effective_cmd = "agy --dangerously-skip-permissions"
    elif preset == "opencode" or command in ("opencode", "--opencode"):
        effective_cmd = "opencode --dangerously-skip-permissions"
    elif command in ("none", "shell", "bash", "sh"):
        effective_cmd = None

    try:
        session = await driver.new_session(session_name, start_dir=start_dir, command=effective_cmd)
        msg = f"Session '{session.name}' created successfully."
        if start_dir:
            msg += f" Directory: {start_dir}."
        if effective_cmd:
            msg += f" Command: {effective_cmd}."
        else:
            msg += " Mode: Bare interactive shell (no command)."
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


@mcp_server.prompt(
    name="tmux_supervise_agent",
    description="Supervise an autonomous AI coding agent (e.g. Antigravity 'agy', OpenCode) running in a tmux session",
)
def tmux_supervise_agent_prompt(session_name: str, task_goal: str = "") -> str:
    """Generate prompt instructions for supervising a CLI agent."""
    goal_clause = f" The stated goal is: '{task_goal}'." if task_goal else ""
    return (
        f"You are supervising an autonomous AI coding agent running in tmux session '{session_name}'.{goal_clause}\n\n"
        "Follow these monitoring and supervisory guidelines:\n"
        f"1. Call `capture_tmux_pane` with `session_name='{session_name}'` and `lines=50` to inspect recent output.\n"
        "2. Analyze whether the agent is actively executing, waiting for user confirmation (e.g. 'y/n', tool confirmation, diff approval), or finished.\n"
        "3. If a confirmation prompt is pending and the action aligns with safety and the task goal, send approval using `send_tmux_keys(session_name, 'y', enter=True)`.\n"
        "4. If an unexpected error or dangerous action is detected, send cancellation using `send_tmux_keys(session_name, 'C-c', enter=False)`.\n"
        "5. Summarize the agent's current activity, status, and your supervisory recommendations clearly."
    )


@mcp_server.prompt(
    name="tmux_quick_approve",
    description="Inspect pending prompt in a tmux session and approve it",
)
def tmux_quick_approve_prompt(session_name: str) -> str:
    """Generate prompt instructions for quick one-touch approval."""
    return (
        f"Please inspect the pending prompt in tmux session '{session_name}'.\n"
        f"1. First call `capture_tmux_pane` for session '{session_name}' with lines=20 to see what confirmation is requested.\n"
        f"2. Confirm what command or action is being approved.\n"
        f"3. Call `send_tmux_keys(session_name='{session_name}', keys='y', enter=True)` to confirm.\n"
        "4. Capture the pane once more to verify the confirmation was accepted and report progress."
    )


@mcp_server.prompt(
    name="tmux_status_summary",
    description="Audit and summarize the state of all host tmux terminal sessions",
)
def tmux_status_summary_prompt() -> str:
    """Generate prompt instructions for inspecting host tmux infrastructure."""
    return (
        "Please audit and summarize the status of all tmux terminal sessions on the host server:\n"
        "1. Call `list_tmux_sessions` to retrieve all active sessions.\n"
        "2. For any sessions currently attached or running autonomous agents, call `capture_tmux_pane` with `lines=15`.\n"
        "3. Present a clean markdown dashboard showing session names, active windows, attachment state, and brief status summaries."
    )


@mcp_server.prompt(
    name="tmux_launch_agent",
    description="Spawn an autonomous coding agent (agy or opencode) with permissions skipped",
)
def tmux_launch_agent_prompt(
    agent_type: str = "agy",
    session_name: str = "",
    start_dir: str = "/containers",
    task_goal: str = "",
) -> str:
    """Generate prompt instructions for launching an autonomous agent in tmux."""
    sess = session_name or f"{agent_type}-task"
    goal_line = (
        f"3. Send the initial goal '{task_goal}' to the session using `send_tmux_keys(session_name='{sess}', keys='{task_goal}', enter=True)`.\n"
        if task_goal
        else ""
    )
    return (
        f"Launch an autonomous {agent_type} agent in a new tmux session:\n"
        f"1. Call `create_tmux_session(session_name='{sess}', start_dir='{start_dir}', preset='{agent_type}')`.\n"
        f"2. Wait 2 seconds, then call `capture_tmux_pane(session_name='{sess}', lines=20)` to verify the TUI initialized.\n"
        f"{goal_line}"
        f"4. Provide the user with the session name `{sess}` so they can attach or monitor via `/peek {sess}`."
    )
