# ROADMAP.md: LibreChatTmuxBridge

Implementation roadmap, endpoint contracts, port allocation, and milestone verification checkpoints.

---

## 🎯 Milestones & Phases

### Phase 1: Core Daemon & Direct Terminal Driving (MVP)
- [ ] Initialize Python package with `uv` (`pyproject.toml`, FastAPI, Uvicorn).
- [ ] Implement `GET /v1/models`:
  - Run `tmux list-sessions -F "#{session_name}"`.
  - Format output as OpenAI-compatible `ModelListResponse` (`id: "tmux:<session_name>"`).
- [ ] Implement `POST /v1/chat/completions`:
  - Extract target session from `model` field.
  - Snapshot pane scrollback baseline via `tmux capture-pane -pt <session> -S -100`.
  - Inject user input via `tmux send-keys -t <session> "<input>" Enter`.
  - Polling loop diffing output every 100–200ms.
  - Stream delta chunks via Server-Sent Events (SSE) wrapped in markdown.
  - Terminate stream with `data: [DONE]` when prompt/idle is detected.
- [ ] Implement `/new <session_name> [dir] [cmd]` session auto-creation handler.

### Phase 2: LibreChat Registration & Verification
- [ ] Add endpoint block to `/containers/ai/librechat/librechat.yaml`:
  ```yaml
  endpoints:
    custom:
      - name: "Tmux Terminal"
        apiKey: "sk-tmux"
        baseURL: "http://10.0.0.10:8035/v1"
        models:
          fetch: true
        titleConvo: true
        modelDisplayLabel: "Tmux Terminal"
  ```
- [ ] Restart LibreChat container: `docker compose restart librechat` in `/containers/ai/librechat`.
- [ ] Verify dynamic model population in LibreChat UI (web & mobile).
- [ ] Test end-to-end streaming with basic shell commands (`docker ps`, `git status`).

### Phase 3: Interactive Agent TUI Verification (`agy` & `opencode`)
- [ ] Launch an active `agy` session in a tmux window:
  ```bash
  tmux new-session -s agy-test -c /containers "agy"
  ```
- [ ] Select `tmux:agy-test` in LibreChat from mobile.
- [ ] Send a conversational prompt: *"Inspect the recent changes in /containers/webservices"*.
- [ ] Verify clean streaming output of thoughts, tool calls, and file diffs in the chat bubble.
- [ ] Verify responding to an interactive confirmation prompt (`y/n`).
- [ ] SSH into the server from desktop workstation; verify `agy-test` is active in the `fzf` picker, attach, and confirm state parity.

### Phase 4: Tmux MCP Copilot Agent Integration (Dual-Mode)
- [ ] Deploy [`nickgnd/tmux-mcp`](https://github.com/nickgnd/tmux-mcp) as a local container or systemd service.
- [ ] Register `tmux-mcp` under `mcpServers` in `librechat.yaml`.
- [ ] Create a "DevOps & Agent Copilot" preset in LibreChat.
- [ ] Test multi-session reasoning, status summaries, and background session supervision from mobile.

---

## 🔌 Port & Network Allocation

Adhering strictly to the **Pipeline Pattern** decades registered in `/containers/productivity/obsidian/shared/Infrastructure/container_mapping.md`:

| Service | Host Port | Internal Port | Protocol | Description |
| :--- | :--- | :--- | :--- | :--- |
| `librechat-tmux-bridge` | **8035** | **8035** | HTTP / SSE | Direct Terminal-to-OpenAI Bridge for LibreChat |
| `cli-agent-dispatch` | 8032 | 8032 | HTTP / SSE | Headless Agent Delegation Gateway (existing) |
| `librechat` | 8451 | 3080 | HTTPS / Web | LibreChat Web & Mobile PWA interface |

---

## 🧪 Verification & Acceptance Criteria

1. **Dynamic Visibility:** Creating a session via `tmux new-session -d -s test-sess` causes `tmux:test-sess` to appear in LibreChat's model dropdown upon refresh.
2. **Zero-Token Streaming:** Interacting with `tmux:test-sess` executes commands instantly without consuming OpenAI or third-party LLM API credits.
3. **Interactive TUI Continuity:** Prompts sent to an active `agy` or `opencode` instance feed into the warm process without spawning new subprocesses or dropping state.
4. **Desktop Continuity:** Running `tmux attach -t <session>` over SSH shows the exact commands and output sent from mobile with full scrollback.
