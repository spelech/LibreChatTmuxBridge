# Configuration and CLI Reference

LibreChatTmuxBridge accepts configuration through environment variables, `.env` configuration files, and command line arguments.

## Environment Variables

All configuration environment variables use the `TMUX_BRIDGE_` prefix:

| Environment Variable | Default Value | Description |
| :--- | :--- | :--- |
| `TMUX_BRIDGE_HOST` | `0.0.0.0` | IP network interface for the daemon listener |
| `TMUX_BRIDGE_PORT` | `8035` | TCP port number for the HTTP and MCP services |
| `TMUX_BRIDGE_API_KEY` | `sk-tmux` | Authorization key required for OpenAI compatibility endpoints |
| `TMUX_BRIDGE_TMUX_BIN` | `tmux` | File path or command name for the tmux executable |
| `TMUX_BRIDGE_TMUX_SOCKET` | None | Absolute path to a custom tmux socket file |
| `TMUX_BRIDGE_MAX_SCROLLBACK_LINES` | `200` | Maximum history lines retrieved per capture cycle |
| `TMUX_BRIDGE_POLL_INTERVAL_SEC` | `0.1` | Sampling interval in seconds for delta calculation |
| `TMUX_BRIDGE_QUIESCENCE_TIMEOUT_SEC` | `0.8` | Inactivity duration in seconds before stream closure |
| `TMUX_BRIDGE_STREAM_TIMEOUT_SEC` | `30.0` | Maximum duration in seconds for an individual completion stream |
| `TMUX_BRIDGE_LOG_LEVEL` | `INFO` | Logging severity threshold (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `TMUX_BRIDGE_MCP_ENABLED` | `true` | Enables the FastMCP endpoint at `/mcp` |

## Command Line Interface Commands

Execute CLI commands with `uv run librechat-tmux-bridge <command>`:

### start

Starts the bridge HTTP daemon:

```bash
uv run librechat-tmux-bridge start [--host 0.0.0.0] [--port 8035] [--reload]
```

### list

Displays all active host tmux sessions:

```bash
uv run librechat-tmux-bridge list
```

### capture

Outputs captured terminal lines from the designated session:

```bash
uv run librechat-tmux-bridge capture <session_name> [--lines 50] [--raw]
```

### send

Transmits keystrokes or commands to the designated session:

```bash
uv run librechat-tmux-bridge send <session_name> "git status" [--no-enter]
```

### version

Prints the installed software version:

```bash
uv run librechat-tmux-bridge version
```

## Systemd Service Configuration

For continuous host execution, configure a systemd user unit at `~/.config/systemd/user/librechat-tmux-bridge.service`:

```ini
[Unit]
Description=LibreChatTmuxBridge Daemon
After=network.target

[Service]
Type=simple
WorkingDirectory=/containers/dev/LibreChatTmuxBridge
ExecStart=/home/steve/.local/bin/uv run librechat-tmux-bridge start --host 0.0.0.0 --port 8035
Restart=on-failure
RestartSec=5s
Environment=TMUX_BRIDGE_HOST=0.0.0.0
Environment=TMUX_BRIDGE_PORT=8035

[Install]
WantedBy=default.target
```

Enable and start the service:

```bash
systemctl --user daemon-reload
systemctl --user enable --now librechat-tmux-bridge.service
```
