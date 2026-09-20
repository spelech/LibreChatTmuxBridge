---
layout: home

hero:
  name: "LibreChatTmuxBridge"
  text: "Bidirectional Host tmux Bridge"
  tagline: "Terminal driver and agentic copilot bridge for LibreChat and persistent tmux sessions."
  actions:
    - theme: brand
      text: Get Started
      link: /guide/getting-started
    - theme: alt
      text: System Architecture
      link: /architecture/overview

features:
  - title: Direct Terminal Driving
    details: Send commands through an OpenAI-compatible endpoint. Terminal output streams back via Server-Sent Events without external API tokens.
  - title: Dynamic Session Discovery
    details: Active host tmux sessions populate the LibreChat model list automatically. Create new sessions dynamically with the slash command interface.
  - title: Agentic Copilot Integration
    details: FastMCP tools allow reasoning models to inspect terminal panes, submit user input, and monitor background tasks.
  - title: Desktop and Mobile Parity
    details: Operate persistent sessions from mobile devices through LibreChat. Attach immediately from desktop workstations over SSH with zero state loss.
---

## System Topology

```mermaid
flowchart TD
    subgraph Mobile ["Mobile Client"]
        LC["LibreChat Interface<br/>(Browser or PWA)"]
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

## Operational Example

Send the list command in LibreChat:

```text
/list
```

The bridge returns active session details:

```markdown
### Active Host Tmux Sessions

| Session | Windows | Attached | Active Window |
| :--- | :--- | :--- | :--- |
| `agy-work` | 1 | Yes | agy |
| `infra` | 2 | No | bash |
```
