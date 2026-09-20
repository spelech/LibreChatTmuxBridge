# Mobile TUI Experience

Using a traditional mobile SSH client (Termius, Blink Shell) on smartphones often leads to frustration:
- Virtual keyboards cover half of the terminal output.
- Navigation keys (`Ctrl`, `Alt`, `Esc`, `Tab`, arrows) require cumbersome secondary toolbars.
- Session disconnects occur whenever you switch apps or lock your screen.

**LibreChatTmuxBridge** turns your smartphone into an intuitive, touch-friendly control console.

---

## 📱 Mobile Slash Commands

LibreChatTmuxBridge provides built-in slash commands that let you control tmux without typing complex terminal commands:

| Command | Arguments | Description |
| :--- | :--- | :--- |
| **`/list`** | None | List active tmux sessions with window counts and attached status |
| **`/new`** | `<name> [dir] [cmd]` | Spawn a new persistent tmux session on the host |
| **`/kill`** | `<name>` | Terminate a tmux session |
| **`/keys`** | `<key>` | Send special modifier keys (e.g. `C-c`, `Escape`, `y`, `n`) |
| **`/help`** | None | Display the interactive command menu |

---

## 🤖 Persistent AI Agent TUIs (`agy`, `opencode`)

When running AI coding assistants like **Antigravity (`agy`)** or **OpenCode**, you don't want to run them as cold, one-off CLI processes. You want them active in a warm TUI REPL:

1. On your phone in LibreChat, send:
   ```text
   /new agy-caddy /containers/webservices "agy"
   ```
2. Switch model to `tmux:agy-caddy`.
3. Send natural instructions:
   ```text
   Review recent changes to Caddyfile and run validation.
   ```
4. As `agy` runs tools, edits files, and reasons, the output streams directly into the chat bubble formatted cleanly.
5. If `agy` prompts for approval:
   ```text
   Proceed with Caddy reload? [y/N]
   ```
   Simply tap the send box and enter:
   ```text
   /keys y
   ```
