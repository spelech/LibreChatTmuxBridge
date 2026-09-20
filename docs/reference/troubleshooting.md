# Troubleshooting & FAQ

Common diagnostic scenarios and resolutions for **LibreChatTmuxBridge**.

---

## 🔍 Common Issues

### 1. `tmux: command not found`
- **Symptom:** Daemon logs show `⚠️ Tmux binary 'tmux' was not found in PATH!`.
- **Cause:** `tmux` is not installed on the system.
- **Resolution:** Install tmux using your package manager:
  ```bash
  sudo apt-get update && sudo apt-get install -y tmux
  ```

---

### 2. LibreChat cannot connect to bridge (`ECONNREFUSED` or 502)
- **Symptom:** LibreChat displays connection failed or model dropdown is empty.
- **Cause:**
  1. The bridge is bound to `127.0.0.1` instead of `0.0.0.0` or `10.0.0.10`.
  2. If LibreChat is running in Docker, `localhost` refers to the container, not the host.
- **Resolution:**
  - Use `http://10.0.0.10:8035/v1` as the `baseURL` in `librechat.yaml`.
  - Ensure `TMUX_BRIDGE_HOST=0.0.0.0`.

---

### 3. "Session already exists" error
- **Symptom:** `/new session_name` returns `Session already exists`.
- **Cause:** A tmux session with that name is already running on the host.
- **Resolution:** Use a different name or terminate the old session with `/kill session_name`.

---

### 4. Terminal output freezes or hangs
- **Symptom:** Command is sent but stream does not end.
- **Cause:** The foreground process in tmux is waiting for user input (e.g. `[y/N]` prompt or pager like `less`).
- **Resolution:**
  - Send response key using `/keys y` or `/keys q` to exit pagers.
  - The bridge automatically times out after `stream_timeout_sec` (default 30s) to prevent infinite loops.
