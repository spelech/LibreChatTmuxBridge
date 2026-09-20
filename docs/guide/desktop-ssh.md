# Desktop SSH Integration

This guide explains how to attach to host tmux sessions from a desktop workstation over SSH.

## System Synchronization

LibreChatTmuxBridge manages native host tmux sessions. Every session created through the mobile LibreChat interface exists directly on the host server.

When you connect to the host workstation over SSH, all mobile sessions are immediately available. You can attach to any session without loss of process state or terminal scrollback.

## Shell Configuration with fzf

Add the following shell function to your `~/.bashrc` file to enable an interactive session selector:

```bash
# Tmux interactive session attach helper
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

Reload the shell configuration:

```bash
source ~/.bashrc
```

## Interactive Session Attachment

Run the `tm` command in your terminal:

```bash
tm
```

The interactive menu displays active host sessions:

```text
ENTER: Attach | CTRL-N: New | CTRL-D: Kill | ESC: Cancel
> 
  agy-caddy        (1 win, detached)
  opencode-api     (2 win, detached)
  infra            (1 win, attached)
```

1. Use arrow keys to navigate the list.
2. Press **Enter** to attach to the selected session.
3. Press **Ctrl+N** to create a new session.
4. Press **Ctrl+D** to terminate the selected session.
5. Press **Escape** to exit without attaching.
