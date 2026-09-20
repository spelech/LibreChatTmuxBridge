# Getting Started

This guide explains how to install and start the LibreChatTmuxBridge daemon on a Linux host.

## Prerequisites

Verify that the host environment satisfies these requirements:

1. **Linux host:** Install `tmux` version 3.2 or later. Run `tmux -V` to confirm the installation.
2. **Python environment:** Install Python 3.12 or later and the `uv` package manager.
3. **LibreChat instance:** Ensure a functional LibreChat instance is accessible on your network.

## Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:spelech/LibreChatTmuxBridge.git
   cd LibreChatTmuxBridge
   ```

2. Synchronize project dependencies:
   ```bash
   uv sync
   ```

## Daemon Execution

Start the daemon with the command line interface:

```bash
uv run librechat-tmux-bridge start --host 0.0.0.0 --port 8035
```

The daemon initializes and displays startup information:

```text
Discovered tmux binary at: /usr/bin/tmux
LibreChatTmuxBridge v0.1.0 listening on http://0.0.0.0:8035
OpenAI endpoint available at: /v1/models and /v1/chat/completions
Model Context Protocol (MCP) server available at: /mcp/sse
```

## Command Line Operations

You can manage sessions directly from the terminal.

1. List all active host sessions:
   ```bash
   uv run librechat-tmux-bridge list
   ```

2. Capture terminal content from a session:
   ```bash
   uv run librechat-tmux-bridge capture <session_name> --lines 30
   ```

3. Send keystrokes or commands to a session:
   ```bash
   uv run librechat-tmux-bridge send <session_name> "docker ps"
   ```

## Health Verification

Send an HTTP request to the health endpoint to confirm daemon status:

```bash
curl -s http://127.0.0.1:8035/health | jq
```

Expected response format:

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "uptime_seconds": 12.45,
  "active_sessions": 3
}
```
