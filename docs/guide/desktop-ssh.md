# Desktop SSH Parity (`fzf` Session Picker)

A primary design pillar of **LibreChatTmuxBridge** is **100% Desktop Parity**. 

Because all commands and sessions run inside real host `tmux` processes:
- Anything you create or execute from your phone in LibreChat is immediately available on your workstation.
- When you sit down at your desk and open an SSH terminal, you can attach to the exact same agent TUI session with a single keystroke.

---

## 🖥️ Shell Configuration (`~/.bashrc`)

Add the following helper function and login trigger to your workstation's `~/.bashrc`:

```bash
# ==========================================
# Tmux fzf Fast Session Attach
# ==========================================
tm() {
  local session
  session=$(tmux list-sessions -F "#{session_name} (#{session_windows} win, #{?session_attached,attached,detached})" 2>/dev/null | \
    fzf --header="ENTER: Attach | CTRL-N: New | CTRL-D: Kill | ESC: Cancel" \
        --bind="ctrl-n:execute(read -p 'Session name: ' s && tmux new-session -d -s \$s)+reload(tmux list-sessions -F '#{session_name} (#{session_windows} win, #{?session_attached,attached,detached})')" \
        --bind="ctrl-d:execute(tmux kill-session -t {1})+reload(tmux list-sessions -F '#{session_name} (#{session_windows} win, #{?session_attached,attached,detached})')")

  if [[ -n "$session" ]]; then
    local sess_name
    sess_name=$(echo "$session" | awk '{print $1}')
    tmux attach-session -t "$sess_name"
  fi
}
```

---

## ⚡ Interactive Workflow

When you SSH into the server:

```text
ENTER: Attach | CTRL-N: New | CTRL-D: Kill | ESC: Cancel
> 
  agy-caddy        (1 win, detached)
  opencode-api     (2 win, detached)
  infra            (1 win, attached)
```

Selecting `agy-caddy` drops you right back into the active agent REPL started on your phone!
