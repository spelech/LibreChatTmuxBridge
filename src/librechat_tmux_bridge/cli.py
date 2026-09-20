"""
Typer CLI entrypoint for LibreChatTmuxBridge.
"""

import asyncio
import sys

import typer
import uvicorn

from librechat_tmux_bridge import __version__
from librechat_tmux_bridge.config import settings
from librechat_tmux_bridge.core.terminal_streamer import clean_terminal_output
from librechat_tmux_bridge.core.tmux_driver import TmuxDriver

app = typer.Typer(
    name="librechat-tmux-bridge",
    help="Universal bidirectional bridge between LibreChat and host tmux multiplexers.",
    add_completion=False,
)


@app.command()
def start(
    host: str = typer.Option(settings.host, "--host", "-h", help="Host interface to bind"),
    port: int = typer.Option(settings.port, "--port", "-p", help="Port to listen on"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload for development"),
):
    """Start the LibreChatTmuxBridge daemon."""
    typer.echo(f"Starting LibreChatTmuxBridge v{__version__} on {host}:{port}...")
    uvicorn.run(
        "librechat_tmux_bridge.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=settings.log_level.lower(),
    )


@app.command(name="list")
def list_sessions():
    """List all running tmux sessions on the host."""
    driver = TmuxDriver(settings)
    sessions = asyncio.run(driver.list_sessions())
    if not sessions:
        typer.echo("No active tmux sessions found.")
        return

    typer.echo(f"Found {len(sessions)} active session(s):")
    for s in sessions:
        att = "attached" if s.attached else "detached"
        win = s.active_window or "bash"
        typer.echo(f"  • {s.name:<18} ({s.windows} win, {att}, active: {win})")


@app.command()
def capture(
    session: str = typer.Argument(..., help="Name of target tmux session"),
    lines: int = typer.Option(50, "--lines", "-n", help="Lines of scrollback to capture"),
    raw: bool = typer.Option(False, "--raw", help="Do not strip ANSI escape codes"),
):
    """Capture and print scrollback buffer from a tmux session."""
    driver = TmuxDriver(settings)
    try:
        output = asyncio.run(driver.capture_pane(session, lines=lines))
        if not raw:
            output = clean_terminal_output(output)
        sys.stdout.write(output + "\n")
        sys.stdout.flush()
    except Exception as ex:
        typer.secho(f"Error: {ex}", fg=typer.colors.RED, err=True)
        sys.exit(1)


@app.command()
def send(
    session: str = typer.Argument(..., help="Name of target tmux session"),
    command: str = typer.Argument(..., help="Command or keys to send"),
    no_enter: bool = typer.Option(False, "--no-enter", help="Do not send Enter key after keys"),
):
    """Send command text or keys to a tmux session."""
    driver = TmuxDriver(settings)
    try:
        asyncio.run(driver.send_keys(session, command, enter=not no_enter))
        typer.echo(f"Successfully sent to '{session}': {command}")
    except Exception as ex:
        typer.secho(f"Error: {ex}", fg=typer.colors.RED, err=True)
        sys.exit(1)


@app.command()
def version():
    """Display daemon version."""
    typer.echo(f"LibreChatTmuxBridge v{__version__}")


if __name__ == "__main__":
    app()
