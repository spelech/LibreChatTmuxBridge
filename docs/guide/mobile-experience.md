# Mobile Terminal Experience

This guide explains how to use LibreChat on mobile devices to monitor and operate persistent tmux sessions.

## Mobile Limitations of Traditional SSH

Traditional mobile SSH applications have operational disadvantages:
- Virtual keyboards obscure terminal output.
- Control keys require multi-touch navigation bars.
- Mobile operating systems terminate background TCP connections when the screen locks.

LibreChatTmuxBridge eliminates these issues. Terminal sessions persist independently on the host server. The mobile interface uses standard HTTP and Server-Sent Events to stream terminal updates.

## Mobile Operational Workflow

You can manage sessions on mobile devices through built-in slash commands:

1. **List Active Sessions:**
   Send `/list` to view running sessions, window counts, and connection states.

2. **Create New Sessions:**
   Send `/new <session_name> [start_directory] [command]` to start a detached session.

3. **Terminate Sessions:**
   Send `/kill <session_name>` to stop an active session.

4. **Send Control Keystrokes:**
   Send `/keys <key_combination>` to transmit special keys such as `C-c` (Interrupt) or `Escape`.

## Operating Interactive Agent Sessions

You can run interactive coding agents such as Antigravity (`agy`) or OpenCode in persistent sessions:

1. Create an agent session:
   ```text
   /agy caddy-work /containers/webservices
   ```

2. Select the new session from the LibreChat model menu:
   ```text
   tmux:caddy-work
   ```

3. Submit instructions to the agent:
   ```text
   Check the Caddyfile configuration and validate syntax.
   ```

4. The bridge streams the terminal output into the chat message bubble.

5. When the agent prompts for confirmation, send approval:
   ```text
   /approve
   ```
