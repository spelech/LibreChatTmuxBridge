# Getting Started

**LibreChatTmuxBridge** runs as a lightweight daemon on your host server or dev workstation.

---

## 📦 Prerequisites

1. **Linux / Unix host** with `tmux` installed (`which tmux`).
2. **Python 3.12+** with `uv` package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`).
3. **LibreChat** instance (running in Docker or bare metal).

---

## 🛠️ Installation

Clone the repository and install dependencies using `uv`:

```bash
git clone git@github.com:spelech/LibreChatTmuxBridge.git
cd LibreChatTmuxBridge
uv sync
```

---

## 🚀 Running the Daemon

You can start the daemon using the provided Typer CLI:

```bash
uv run librechat-tmux-bridge start --host 0.0.0.0 --port 8035
```

Output:
```text
Discovered tmux binary at: /usr/bin/tmux
LibreChatTmuxBridge v0.1.0 listening on http://0.0.0.0:8035
OpenAI endpoint available at: /v1/models and /v1/chat/completions
Model Context Protocol (MCP) server available at: /mcp/sse
```

---

## 🧪 Testing the CLI

Check active sessions on your server:

```bash
uv run librechat-tmux-bridge list
```

Capture the latest 30 lines of scrollback:

```bash
uv run librechat-tmux-bridge capture <session_name> --lines 30
```

Inject a command into a session:

```bash
uv run librechat-tmux-bridge send <session_name> "docker ps"
```

---

## 🩺 Verifying Health

Query the health probe via curl:

```bash
curl -s http://127.0.0.1:8035/health | jq
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 12.45,
  "active_sessions": 3
}
```
