# Architectural Overview

**LibreChatTmuxBridge** resolves the tension between dumb terminal pipes and stateless cloud agent APIs by unifying them into a local, dual-mode bridge.

---

## 🏛️ The Dual-Mode Paradigm

| Dimension | Mode 1: Direct Terminal Driver (Pseudo-LLM) | Mode 2: Agentic Copilot (FastMCP) |
| :--- | :--- | :--- |
| **Backend Route** | `POST /v1/chat/completions` (SSE Stream) | Model Context Protocol (`/mcp/sse`) |
| **Token Cost** | **Zero tokens** (100% free & local) | Standard LLM turn tokens |
| **Latency** | Instant (~50–100ms) | Reasoning delay (2–4s) |
| **Output Format** | Live streaming terminal text inside clean Markdown | Synthesized natural language summary & structured tool calls |
| **Primary Use Case** | Typing commands into shells, approving TUI prompts, live monitoring | Multi-session audits, cross-project troubleshooting, autonomous workflows |

---

## 🏗️ Architectural Topology

```mermaid
flowchart TD
    subgraph Clients ["Clients"]
        LC["LibreChat PWA (:8451)<br/>(Mobile / Tablet / Browser)"]
        SSH["Desktop SSH Terminal<br/>(tmux attach via fzf)"]
    end

    subgraph BridgeDaemon ["LibreChatTmuxBridge Daemon (:8035)"]
        API["FastAPI App (uvicorn)"]
        OAI["OpenAI Endpoint Router<br/>• GET /v1/models<br/>• POST /v1/chat/completions"]
        MCP["FastMCP Server (/mcp)<br/>• list_sessions<br/>• capture_pane<br/>• send_keys<br/>• new_session<br/>• kill_session"]
        STREAM["TerminalStreamer<br/>• Screen Grid Capture<br/>• Delta Line Differ<br/>• ANSI Filter & Quiescence"]
        DRIVER["TmuxDriver (Subprocess CLI)<br/>• list-sessions<br/>• capture-pane<br/>• send-keys<br/>• new-session"]
        TAPS["Diagnostic Taps & Ring Buffer"]
    end

    subgraph HostTmux ["Host Terminal Multiplexer (tmux)"]
        S1["tmux: 'agy-work'<br/>[Active agy TUI]"]
        S2["tmux: 'opencode'<br/>[Active OpenCode TUI]"]
        S3["tmux: 'infra'<br/>[Active Shell / Docker]"]
    end

    LC -->|Mode 1: /v1/chat/completions SSE| OAI
    LC -->|Mode 2: MCP Tools SSE| MCP
    OAI --> STREAM
    MCP --> DRIVER
    STREAM --> DRIVER
    DRIVER --> HostTmux
    SSH -.->|Direct host attach| HostTmux
```

---

## 🔒 Security & Network Boundary

- **Host Port:** `8035` (adheres strictly to the Pipeline Pattern decades).
- **Network Scope:** Bound locally to `10.0.0.10:8035` or Docker internal network (`net_mcp`).
- **Access Control:** Guarded behind PocketID / TinyAuth SSO via LibreChat reverse proxy.
- **Zero Cloud Exposure:** No inbound open WAN ports, zero external relay servers.
