# LibreChatTmuxBridge

[![CI Quality Gates](https://github.com/spelech/LibreChatTmuxBridge/actions/workflows/ci.yml/badge.svg)](https://github.com/spelech/LibreChatTmuxBridge/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/Coverage-94%25-brightgreen.svg)](#test-coverage-and-simulation)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/Docs-GitHub%20Pages-646cff.svg)](https://spelech.github.io/LibreChatTmuxBridge/)

Universal bidirectional bridge between LibreChat and host tmux terminal multiplexers. The bridge provides zero-token terminal streaming and FastMCP agent orchestration for persistent command line sessions and AI agent interfaces.

---

## Technical Overview

Operating terminal sessions from mobile devices using standard SSH clients presents operational constraints:
- On-screen keyboards obstruct terminal display area.
- Control key combinations require complex secondary menus.
- Mobile operating systems terminate background SSH connections during app switches.
- Running agent processes in cold headless subprocesses discards conversational context.

LibreChatTmuxBridge resolves these constraints:
1. **Direct Terminal Streaming:** Uses an OpenAI-compatible `/v1/chat/completions` endpoint to send commands directly to tmux panes with zero token cost.
2. **Dynamic Session Discovery:** Queries `tmux list-sessions` to populate the LibreChat model selector with running sessions.
3. **Session Management:** Creates and terminates detached tmux sessions through interactive slash commands.
4. **Agentic Copilot:** Provides FastMCP tools (`/mcp/sse`) allowing reasoning models to inspect terminal buffers and supervise processes.
5. **Desktop SSH Parity:** Maintains native host tmux sessions, allowing instant attachment from desktop workstations over SSH.

---

## System Topology

```mermaid
flowchart TD
    subgraph Mobile ["Mobile Client"]
        LC["LibreChat Interface (:8451)<br/>(Browser or PWA)"]
    end

    subgraph Bridges ["Bridge Layer"]
        OAI_BRIDGE["Tmux-OpenAI Bridge (:8035)<br/>(/v1/models, /v1/chat/completions)"]
        TMUX_MCP["FastMCP Server (:8035/mcp)<br/>(Streamable HTTP / SSE)"]
    end

    subgraph Multiplexer ["Host Terminal Multiplexer"]
        SESS_AGY["tmux: agy-work<br/>(Antigravity TUI)"]
        SESS_OC["tmux: opencode<br/>(OpenCode TUI)"]
        SESS_SHELL["tmux: infra<br/>(Host Shell)"]
    end

    subgraph Workstation ["Desktop Workstation"]
        FZF["Host Terminal Client<br/>(tmux attach via fzf)"]
    end

    LC -->|"Direct Mode: /v1/chat/completions"| OAI_BRIDGE
    LC -->|"Agentic Mode: MCP Tool Calls"| TMUX_MCP

    OAI_BRIDGE -->|"tmux send-keys and capture-pane"| Multiplexer
    TMUX_MCP -->|"tmux control commands"| Multiplexer

    FZF -->|"tmux attach-session"| Multiplexer
```

---

## Quick Start

### 1. Installation

```bash
git clone git@github.com:spelech/LibreChatTmuxBridge.git
cd LibreChatTmuxBridge
uv sync
```

### 2. Start the Daemon

```bash
uv run librechat-tmux-bridge start --host 0.0.0.0 --port 8035
```

### 3. Connect LibreChat

Add the configuration block to `librechat.yaml`:

```yaml
endpoints:
  custom:
    - name: "Tmux Terminal"
      apiKey: "sk-tmux"
      baseURL: "http://10.0.0.10:8035/v1"
      models:
        default:
          - tmux:new
        fetch: true
      titleConvo: true
      modelDisplayLabel: "Host Tmux"
      dropParams:
        - stop
        - temperature

mcpSettings:
  allowedAddresses:
    - 10.0.0.10:8035

mcpServers:
  tmux-bridge:
    type: sse
    url: http://10.0.0.10:8035/mcp/sse
```

Restart the LibreChat service:

```bash
docker compose restart librechat
```

---

## Built-In Slash Commands

| Command | Usage | Description |
| :--- | :--- | :--- |
| `/list` | `/list` | Display active sessions with window counts and status |
| `/new` | `/new <name> [dir] [cmd]` | Create a detached session on the host |
| `/kill` | `/kill <name>` | Terminate a tmux session |
| `/keys` | `/keys <combo>` | Send control keys (`C-c`, `Escape`, `y`, `Enter`) |
| `/help` | `/help` | Display command reference list |

---

## Test Coverage and Simulation

- **Code Coverage:** Maintained at $\ge 94\%$ statement coverage enforced through `pytest-cov`.
- **Simulation Harness:** 50-turn closed-loop stress test with disturbance injection.
- **Integration Testing:** Direct execution against the host `/usr/bin/tmux` binary.

Run the test suite:

```bash
uv run pytest
```

---

## Technical Documentation

Interactive documentation is hosted on the Agent Preview Hub:
- **Documentation Portal:** [https://spelech.github.io/LibreChatTmuxBridge/](https://spelech.github.io/LibreChatTmuxBridge/)
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — Architectural specifications and pipeline design
- [`REQUIREMENTS.md`](REQUIREMENTS.md) — Traceability matrix and operational constraints
- [`CHANGELOG.md`](CHANGELOG.md) — Version history and release notes
- [`ROADMAP.md`](ROADMAP.md) — Implementation roadmap
