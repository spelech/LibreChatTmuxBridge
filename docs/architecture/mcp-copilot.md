# Agentic MCP Copilot Architecture

The Model Context Protocol (MCP) copilot mode enables external reasoning models (such as Claude or Gemini) to supervise and orchestrate host tmux sessions.

In this mode, LibreChat acts as an intelligent supervisor. The model can inspect active panes across multiple sessions, identify pending approval dialogs, and submit keystrokes on behalf of the user.

## Sequence Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User in LibreChat
    participant LC as Reasoning Model (LibreChat)
    participant MCP as FastMCP Server (:8035/mcp)
    participant TM as Host tmux Multiplexer

    User->>LC: Are any background agent sessions waiting for approval?
    LC->>MCP: list_tmux_sessions()
    MCP->>TM: tmux list-sessions
    TM-->>MCP: Active sessions list
    MCP-->>LC: JSON sessions array
    LC->>MCP: capture_tmux_pane(session_name="agy-caddy", lines=30)
    MCP->>TM: tmux capture-pane -pt agy-caddy -S -30
    TM-->>MCP: Terminal screen buffer
    MCP-->>LC: Plaintext buffer
    Note over LC: Model detects confirmation prompt in terminal output
    LC-->>User: Session agy-caddy is requesting permission to reload Caddy. Approve?
    User->>LC: Yes, approve.
    LC->>MCP: send_tmux_keys(session_name="agy-caddy", keys="y", enter=true)
    MCP->>TM: tmux send-keys -t agy-caddy y Enter
    LC-->>User: Approved. agy is continuing execution.
```

## FastMCP Server Capabilities

The bridge implements a FastMCP server over Server-Sent Events (`/mcp/sse`) and HTTP streams.

The server provides these primary capabilities:
1. **Session Inspection:** External agents can query session lists, window identifiers, and attachment states.
2. **Buffer Analysis:** External agents can read arbitrary line counts from the active pane buffer to determine process state.
3. **Keystroke Transmission:** External agents can transmit literal strings or control keys to interact with running programs.
4. **Lifecycle Control:** External agents can spawn new sessions in specified working directories or terminate completed sessions.
