# FastMCP Tools Reference

The bridge implements a Model Context Protocol (MCP) server accessible at `/mcp/sse`. Language models connect to this endpoint to execute terminal tools and supervise sessions.

## Available MCP Tools

### list_tmux_sessions

Returns an array of all active host tmux sessions.

- **Parameters:** None.
- **Return Type:** JSON object.
- **Example Response:**
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

### capture_tmux_pane

Captures text lines from the active pane of the specified tmux session.

- **Parameters:**
  - `session_name` (string, required): The target session name.
  - `lines` (integer, optional, default: `100`): The number of scrollback lines to capture.
  - `strip_escape_codes` (boolean, optional, default: `true`): Strips ANSI escape sequences.
- **Return Type:** Plain text string containing the terminal pane contents.

### send_tmux_keys

Transmits keystrokes, text input, or special control keys to the target session.

- **Parameters:**
  - `session_name` (string, required): The target session name.
  - `keys` (string, required): The characters or key sequences to transmit (for example, `ls -la`, `C-c`, `Escape`, `y`).
  - `enter` (boolean, optional, default: `true`): Appends a carriage return (`Enter`) to the key sequence.
- **Return Type:** Confirmation message string.

### create_tmux_session

Initializes a new detached tmux session on the host.

- **Parameters:**
  - `session_name` (string, required): Unique identifier for the new session.
  - `start_dir` (string, optional): Initial working directory path for the session.
  - `command` (string, optional): Startup command to execute (for example, `agy --dangerously-skip-permissions`).
- **Return Type:** Confirmation status string.

### kill_tmux_session

Terminates the specified tmux session and releases associated processes.

- **Parameters:**
  - `session_name` (string, required): The name of the session to terminate.
- **Return Type:** Confirmation status string.

### execute_tmux_command

Executes arbitrary tmux CLI arguments for low-level automation.

- **Parameters:**
  - `command_args` (string, required): The argument string passed directly to the `tmux` binary.
- **Return Type:** JSON object containing `success`, `exit_code`, `stdout`, and `stderr`.
