# FastMCP Tools Reference

The bridge exposes a standard **Model Context Protocol (MCP)** endpoint mounted at `/mcp/sse`.

---

## 🛠️ Available Tools

### 1. `list_tmux_sessions`
Lists all active host tmux sessions.

- **Parameters:** None
- **Returns:**
  ```json
  {
    "status": "ok",
    "sessions": [
      {
        "name": "agy-work",
        "windows": 1,
        "created": 1700000000,
        "attached": false,
        "active_window": "agy"
      }
    ]
  }
  ```

---

### 2. `capture_tmux_pane`
Captures scrollback lines from a session.

- **Parameters:**
  - `session_name` (string, required): Name of target session.
  - `lines` (integer, optional, default `100`): History lines to capture.
  - `strip_escape_codes` (boolean, optional, default `true`): Strips ANSI codes.
- **Returns:** Clean text buffer from terminal pane.

---

### 3. `send_tmux_keys`
Sends text or commands to a tmux session.

- **Parameters:**
  - `session_name` (string, required): Name of target session.
  - `keys` (string, required): Keystroke text or modifier.
  - `enter` (boolean, optional, default `true`): Whether to press Enter.
- **Returns:** Confirmation message.

---

### 4. `create_tmux_session`
Initializes a new detached session on the host.

- **Parameters:**
  - `session_name` (string, required): Unique name for new session.
  - `start_dir` (string, optional): Directory path to initialize in.
  - `command` (string, optional): Command or process to launch (e.g. `agy`, `opencode`).
- **Returns:** Confirmation status.

---

### 5. `kill_tmux_session`
Destroys a running tmux session.

- **Parameters:**
  - `session_name` (string, required): Name of session to terminate.
- **Returns:** Confirmation status.

---

### 6. `execute_tmux_command`
Safely runs a tmux CLI subcommand.

- **Parameters:**
  - `command_args` (string, required): Command arguments string.
- **Returns:** JSON object containing `success`, `exit_code`, `stdout`, `stderr`.
