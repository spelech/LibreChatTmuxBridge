---
layout: home

hero:
  name: "LibreChatTmuxBridge"
  text: "Mobile-First Host tmux Bridge"
  tagline: "Zero-token streaming terminal driver & agentic copilot bridge for LibreChat and persistent AI agent TUIs (Antigravity agy, OpenCode)."
  actions:
    - theme: brand
      text: Get Started
      link: /guide/getting-started
    - theme: alt
      text: System Architecture
      link: /architecture/overview

features:
  - icon: ⚡
    title: Zero-Token Terminal Driving
    details: Send commands via OpenAI /v1/chat/completions; terminal deltas stream live back via SSE in clean Markdown without third-party API tokens.
  - icon: 🔄
    title: Dynamic Session Discovery
    details: Automatically maps active host tmux sessions into LibreChat's model dropdown. Spawn new persistent sessions on the fly with /new.
  - icon: 🤖
    title: Dual-Mode Copilot (MCP)
    details: Native FastMCP server enables full reasoning models (Claude / Gemini) to inspect panes, send approvals, and supervise multiple background sessions.
  - icon: 📱
    title: Mobile & Desktop Parity
    details: Type comfort on mobile with voice input and Markdown rendering; instant 1-key desktop fzf terminal attach over SSH with zero state loss.
---

## 🌟 High-Level Topology

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

## 🚀 Quick Example

Sending a command in LibreChat:

```text
/list
```

Response:
```markdown
### 🖥️ Active Host Tmux Sessions

| Session | Windows | Attached | Active Window |
| :--- | :--- | :--- | :--- |
| `agy-work` | 1 | ✅ Yes | agy |
| `infra` | 2 | No | bash |
```
