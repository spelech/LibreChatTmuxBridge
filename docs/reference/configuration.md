# Configuration & CLI Reference

LibreChatTmuxBridge is configured using environment variables (with `TMUX_BRIDGE_` prefix) or `.env` files.

---

## ⚙️ Environment Variables

| Variable | Default | Description |
| :--- | :--- | :--- |
| `TMUX_BRIDGE_HOST` | `0.0.0.0` | Host interface to bind server |
| `TMUX_BRIDGE_PORT` | `8035` | Port to listen on (Pipeline Pattern 8035) |
| `TMUX_BRIDGE_API_KEY` | `sk-tmux` | Expected API key in Authorization header |
| `TMUX_BRIDGE_TMUX_BIN` | `tmux` | Command or path to tmux binary |
| `TMUX_BRIDGE_TMUX_SOCKET` | `None` | Optional custom tmux socket path (`-S`) |
| `TMUX_BRIDGE_MAX_SCROLLBACK_LINES` | `200` | History lines to capture from pane |
| `TMUX_BRIDGE_POLL_INTERVAL_SEC` | `0.1` | Polling interval for terminal delta diffing |
| `TMUX_BRIDGE_QUIESCENCE_TIMEOUT_SEC` | `0.8` | Silence timeout before closing turn |
| `TMUX_BRIDGE_STREAM_TIMEOUT_SEC` | `30.0` | Hard safety timeout for streaming |
| `TMUX_BRIDGE_LOG_LEVEL` | `INFO` | Application log level (`DEBUG`, `INFO`, etc.) |
| `TMUX_BRIDGE_MCP_ENABLED` | `true` | Enable FastMCP endpoint at `/mcp` |

---

## 💻 CLI Commands

Run commands using `uv run librechat-tmux-bridge <command>`:

### `start`
Launches the daemon process:
```bash
uv run librechat-tmux-bridge start [--host 0.0.0.0] [--port 8035] [--reload]
```

### `list`
Lists running tmux sessions:
```bash
uv run librechat-tmux-bridge list
```

### `capture`
Prints pane scrollback:
```bash
uv run librechat-tmux-bridge capture <session> [--lines 50] [--raw]
```

### `send`
Injects command or keys into a session:
```bash
uv run librechat-tmux-bridge send <session> "git status" [--no-enter]
```

### `version`
Displays version:
```bash
uv run librechat-tmux-bridge version
```
