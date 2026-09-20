# Troubleshooting and Diagnostics

This reference table outlines common operational faults, diagnostic causes, and corrective actions.

## Diagnostic Matrix

| Condition | Probable Cause | Corrective Action |
| :--- | :--- | :--- |
| **`tmux: command not found`** | The `tmux` executable is not present in the system PATH. | Install tmux with your package manager: `sudo apt-get install -y tmux`. |
| **Connection Refused (`ECONNREFUSED`)** | Daemon is bound to loopback `127.0.0.1` while LibreChat runs inside Docker. | Set `TMUX_BRIDGE_HOST=0.0.0.0` and configure `baseURL: http://10.0.0.10:8035/v1` in `librechat.yaml`. |
| **Session already exists** | A tmux session with the requested identifier is already active. | Choose a unique session identifier or terminate the existing session with `/kill <name>`. |
| **Stream does not terminate** | The interactive program in tmux is waiting for user confirmation or pager exit. | Submit the required key with `/approve`, `/reject`, or `/keys q`. The daemon terminates inactive streams after 30 seconds. |
| **Authentication failure (`401 Unauthorized`)** | The Bearer token in the request does not match `TMUX_BRIDGE_API_KEY`. | Verify that `apiKey: sk-tmux` in `librechat.yaml` matches the server configuration. |
| **Model list is empty in LibreChat** | LibreChat cannot reach `/v1/models` or daemon is not running. | Verify daemon health with `curl -s http://10.0.0.10:8035/health`. Restart the LibreChat container after network changes. |

## Diagnostic Logging and Taps

The daemon provides diagnostic introspection for active sessions and streaming events:

1. **Verify daemon health:**
   ```bash
   curl -s http://127.0.0.1:8035/health | jq
   ```

2. **Inspect recent diagnostic events:**
   ```bash
   curl -s http://127.0.0.1:8035/taps | jq
   ```

3. **Check systemd service status:**
   ```bash
   systemctl --user status librechat-tmux-bridge.service
   ```

4. **Follow live daemon logs:**
   ```bash
   journalctl --user -u librechat-tmux-bridge.service -f
   ```
