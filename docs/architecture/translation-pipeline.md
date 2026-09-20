# TUI Translation Pipeline

Interactive terminal applications (`agy`, `opencode`, `vim`, `htop`) output rich VT100 control codes:
- Cursor addressing (`\x1b[H`, `\x1b[2;5f`)
- Line clearing (`\x1b[2K`)
- Alternate screen buffers (`\x1b[?1049h`)
- Progress spinners that rewrite the same line repeatedly.

Sending raw terminal bytes into a chat UI results in illegible dumps. **LibreChatTmuxBridge** processes terminal streams through a three-stage translation pipeline:

---

## ⚙️ The Three Pipeline Stages

```
┌─────────────────────────────────────────────────────────────┐
│                 Stage 1: Screen Grid Capture                │
│   `tmux capture-pane -pt <session> -S -<history_lines>`     │
│   • tmux resolves cursor addressing and line overwrites     │
│   • Produces an 80-column normalized text buffer            │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Stage 2: Delta Line Differ                  │
│   • Compares the new snapshot against the baseline snapshot │
│   • Filters out volatile progress spinners / redraw noise   │
│   • Isolates newly completed text lines, diffs, and prompts │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Stage 3: ANSI ➔ Markdown Filter             │
│   • Strips residual control bytes (\x1b[...)                │
│   • Wraps terminal logs and code changes in ```bash blocks  │
│   • Emits standard SSE chunks to LibreChat                  │
└─────────────────────────────────────────────────────────────┘
```

---

## ⏱️ Quiescence & Stream Termination

Because a shell command or agent turn does not emit an explicit "EOF" signal, the streamer employs **quiescence detection**:
1. When input is injected, the streamer captures baseline scrollback.
2. Every `poll_interval_sec` (e.g. 100ms), a snapshot is taken.
3. If new lines appear, they are emitted as SSE delta chunks, and `last_change_time` is updated.
4. When `quiescence_timeout_sec` (e.g. 800ms) elapses with no new output, the output is considered settled.
5. The final `finish_reason: "stop"` chunk and `data: [DONE]` sentinel are emitted, returning control to the user.
