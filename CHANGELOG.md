# 📝 Changelog

All notable changes to **LibreChatTmuxBridge** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-09-20

### Added
- Initial project scaffolding adhering to `AgenticEngineeringToolbelt` standards (`python-fastapi-mcp` archetype).
- Dynamic tmux session discovery via `GET /v1/models` (`tmux:<session>` and `tmux:new`).
- Real-time zero-token terminal driving via `POST /v1/chat/completions` (OpenAI-compatible SSE streaming and non-streaming).
- Subprocess-based `TmuxDriver` supporting session creation, deletion, pane capture, and key injection.
- Three-stage terminal translation pipeline: Screen Grid Capture, Delta Line Differ, and ANSI-to-Markdown filter.
- Mobile slash command engine (`/new`, `/kill`, `/list`, `/keys`, `/clear`, `/help`).
- Native FastMCP server at `/mcp` exposing `list_tmux_sessions`, `capture_tmux_pane`, `send_tmux_keys`, `create_tmux_session`, `kill_tmux_session`, and `execute_tmux_command`.
- Diagnostic tap points, circular ring buffers, and 6-part agent feedback envelope for test observability.
- High-volume simulation test harness and real host tmux integration test suite ($\ge 80\%$ code coverage).
- VitePress documentation website with Mermaid topology diagrams, setup guides, and API references.
- 4-stage GitHub Actions CI pipeline and release verification engine (`verify_release.py`, `commit.sh`).
- Systemd service unit and Docker deployment configuration.
