# Agentic MCP Copilot

While Mode 1 gives you instant zero-token driving of individual tmux sessions, **Mode 2 (Agentic Copilot)** lets full reasoning models (Claude 3.7 Sonnet, Gemini 2.5 Flash, DeepSeek V3) orchestrate your homelab and supervise multiple sessions.

---

## 🔄 Interaction Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User on Mobile (LibreChat)
    participant LC as LibreChat Agent (Gemini/Claude)
    participant MCP as FastMCP Server (:8035/mcp)
    participant TM as Host tmux

    User->>LC: "Are any of my background agent sessions waiting for approval?"
    LC->>MCP: list_tmux_sessions()
    MCP->>TM: tmux list-sessions
    TM-->>MCP: Sessions list
    MCP-->>LC: Sessions JSON
    LC->>MCP: capture_tmux_pane(session_name="agy-caddy", lines=30)
    MCP->>TM: tmux capture-pane -pt agy-caddy -S -30
    TM-->>MCP: Terminal screen buffer
    MCP-->>LC: Buffer text
    Note over LC: LLM analyzes buffer: detects confirmation prompt in agy
    LC-->>User: "Session 'agy-caddy' is asking for confirmation to reload Caddyfile. Should I approve?"
    User->>LC: "Yes, approve it."
    LC->>MCP: send_tmux_keys(session_name="agy-caddy", keys="y", enter=true)
    MCP->>TM: tmux send-keys -t agy-caddy "y" Enter
    LC-->>User: "Approved. agy is now applying changes and running reload."
```

---

## 🛠️ MCP Tools Exposed

1. **`list_tmux_sessions`**: Returns all active host sessions with window counts and attached status.
2. **`capture_tmux_pane`**: Fetches clean terminal scrollback up to `N` lines.
3. **`send_tmux_keys`**: Injects text, commands, or single approval characters (`y/n`).
4. **`create_tmux_session`**: Spawns detached sessions with working directory and optional bootstrap command.
5. **`kill_tmux_session`**: Terminates a session.
6. **`execute_tmux_command`**: Runs arbitrary `tmux` subcommands for advanced scripting.
