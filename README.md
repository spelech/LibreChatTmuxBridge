# LibreChatTmuxBridge

[![CI Quality Gates](https://github.com/spelech/LibreChatTmuxBridge/actions/workflows/ci.yml/badge.svg)](https://github.com/spelech/LibreChatTmuxBridge/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/badge/Coverage-94%25-brightgreen.svg)](#-test-coverage--simulation)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docs](https://img.shields.io/badge/Docs-VitePress-646cff.svg)](https://preview.wileyriley.com/librechat-tmux-bridge/)

Universal bidirectional bridge between **LibreChat (Mobile / PWA)** and **host terminal multiplexers (tmux)** for seamless remote terminal interaction and persistent **AI agent TUIs (Antigravity `agy`, OpenCode)**.

---

## 🌟 Executive Summary & Motivation

Interacting with development environments and Linux homelabs from mobile devices (iOS/Android) via mobile SSH clients (e.g. Termius, Blink Shell) has severe usability hurdles:
- **Touch-screen typing friction:** Virtual keyboards cover half the viewport; modifier keys (`Ctrl`, `Alt`, `Esc`, `Tab`, arrows) require awkward multi-touch toolbars.
- **Connection timeouts:** Locking the screen or switching apps terminates SSH connections, dropping context and requiring reconnects.
- **Stateless Agent Silos:** Calling agent CLIs as one-off headless subprocesses (`agy -p` or `opencode run`) destroys the conversational in-memory context and prevents attaching to the session from desktop.
- **The TUI Imperative:** Developers want to work **inside the full interactive TUI (Text User Interface / REPL)** of agents like Antigravity (`agy`) and OpenCode, keeping the agent process warm and interactive 24/7.

**LibreChatTmuxBridge** solves this by turning **LibreChat** into a direct, zero-token, real-time terminal driver and intelligent agent orchestrator:
1. **Direct Terminal Streaming (Zero Tokens, Zero Latency):** Connects to LibreChat via an OpenAI-compatible `/v1/chat/completions` pseudo-LLM endpoint. Messages sent in chat are injected into a live `tmux` pane via `tmux send-keys`, and the terminal output streams back in real-time as the "assistant" response.
2. **Dynamic Session Discovery:** Queries `tmux list-sessions` to dynamically populate LibreChat's model dropdown with active terminal sessions (e.g. `tmux:agy-work`, `tmux:opencode-api`, `tmux:infra`).
3. **Mobile Session Creation:** Allows spawning new persistent tmux sessions from your phone via chat commands (`/new <session> [dir] [cmd]`).
4. **Agentic Copilot Mesh:** Complements direct terminal driving with FastMCP (`/mcp/sse`) so that full LLM agents (Claude / Gemini) can inspect, reason across, and orchestrate multiple tmux sessions on your behalf.
5. **100% Desktop / SSH Parity:** Because all work takes place in real `tmux` sessions on the host, any session created or controlled on mobile is immediately visible and attachable via your desktop SSH `fzf` tmux picker.

---

## 🏗️ High-Level Topology

```mermaid
flowchart TD
    subgraph Mobile ["Mobile Client (Phone / Tablet / Browser)"]
        LC["LibreChat PWA (:8451)<br/>(Voice, Markdown, Dark Mode, History)"]
    end

    subgraph Bridges ["Bridge Layer (Local Daemon on Homelab)"]
        OAI_BRIDGE["Tmux-OpenAI Bridge (:8035)<br/>(/v1/models, /v1/chat/completions)"]
        TMUX_MCP["FastMCP Server (:8035/mcp)<br/>(Streamable HTTP / SSE)"]
    end

    subgraph Multiplexer ["Host Terminal Multiplexer (tmux)"]
        SESS_AGY["tmux: 'agy-work'<br/>[Active Interactive agy TUI]"]
        SESS_OC["tmux: 'opencode'<br/>[Active OpenCode TUI]"]
        SESS_SHELL["tmux: 'infra'<br/>[Active Bash / Docker Shell]"]
    end

    subgraph Workstation ["Desktop / Workstation (SSH)"]
        FZF["~/.bashrc fzf Session Picker<br/>(Immediate 1-key attach)"]
    end

    LC -->|Mode 1: Direct Terminal Driving (Zero Tokens)| OAI_BRIDGE
    LC -->|Mode 2: Agentic Synthesis (Gemini/Claude + Tools)| TMUX_MCP

    OAI_BRIDGE -->|tmux send-keys / capture-pane| Multiplexer
    TMUX_MCP -->|tmux execute-command / capture-pane| Multiplexer

    FZF -->|tmux attach-session| Multiplexer
```

---

## 🚀 Quick Start

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

Add to `librechat.yaml`:

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

Restart LibreChat:
```bash
docker compose restart librechat
```

---

## 📱 In-Chat Slash Commands

| Command | Usage | Description |
| :--- | :--- | :--- |
| `/list` | `/list` | List active sessions with window count and status |
| `/new` | `/new <name> [dir] [cmd]` | Spawn a new detached session on host |
| `/kill` | `/kill <name>` | Terminate a tmux session |
| `/keys` | `/keys <combo>` | Send special keys (`C-c`, `Escape`, `y`, `Enter`) |
| `/help` | `/help` | Show command menu |

---

## 🧪 Test Coverage & Simulation

- **Coverage:** $\ge 94\%$ statement coverage enforced via `pytest-cov`.
- **Simulation Harness:** 50-turn closed-loop stress test with disturbance injection.
- **Real Tmux Integration:** Empirical E2E testing against host `/usr/bin/tmux`.

Run the test suite:
```bash
uv run pytest
```

---

## 📚 Living Documentation

Interactive VitePress documentation is available locally and on the Agent Preview Hub:
- **Live Preview:** [https://preview.wileyriley.com/librechat-tmux-bridge/](https://preview.wileyriley.com/librechat-tmux-bridge/)
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — Comprehensive technical architecture
- [`REQUIREMENTS.md`](REQUIREMENTS.md) — Requirements traceability matrix
- [`CHANGELOG.md`](CHANGELOG.md) — Semantic version history
- [`ROADMAP.md`](ROADMAP.md) — Implementation roadmap
