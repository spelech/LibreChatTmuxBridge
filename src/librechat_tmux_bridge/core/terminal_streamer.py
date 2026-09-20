"""
Terminal stream processor, ANSI filter, delta differ, and slash command dispatcher.
"""

import asyncio
import json
import logging
import re
import shlex
import time
from collections.abc import AsyncGenerator

from librechat_tmux_bridge.config import BridgeConfig, settings
from librechat_tmux_bridge.core.models import (
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatDelta,
)
from librechat_tmux_bridge.core.tmux_driver import ITmuxDriver

logger = logging.getLogger(__name__)

# Regex to strip ANSI escape sequences, VT100 cursor movement, colors, etc.
ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes and normalize whitespace."""
    return ANSI_ESCAPE_RE.sub("", text)


def clean_terminal_output(raw_text: str) -> str:
    """Clean terminal raw text, stripping ANSI and normalizing trailing blank lines."""
    cleaned = strip_ansi(raw_text)
    # Remove carriage returns
    cleaned = cleaned.replace("\r", "")
    # Trim trailing whitespace on each line
    lines = [line.rstrip() for line in cleaned.splitlines()]
    # Remove trailing blank lines
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


class TerminalStreamer:
    """Manages terminal driving, delta diffing, and SSE stream generation."""

    def __init__(self, driver: ITmuxDriver, config: BridgeConfig | None = None):
        self.driver = driver
        self.config = config or settings

    def parse_slash_command(self, text: str) -> tuple[str, list[str]] | None:
        """Check if message is a slash command and return (command, args)."""
        text = text.strip()
        if not text.startswith("/"):
            return None

        parts = shlex.split(text)
        if not parts:
            return None

        cmd = parts[0][1:].lower()
        args = parts[1:]
        return cmd, args

    async def handle_slash_command(self, cmd: str, args: list[str]) -> str:
        """Execute built-in bridge slash commands."""
        if cmd == "help":
            return (
                "### 📟 LibreChat Tmux Bridge Commands\n\n"
                "- `/new <name> [dir] [cmd]` - Create a new detached tmux session\n"
                "- `/kill <name>` - Terminate a tmux session\n"
                "- `/list` - List active tmux sessions\n"
                "- `/keys <keys>` - Send special keys (e.g. `C-c`, `C-d`, `Escape`, `Up`, `Down`)\n"
                "- `/clear` - Clear scrollback on target session\n"
                "- `/help` - Show this help menu\n"
            )

        if cmd == "list":
            sessions = await self.driver.list_sessions()
            if not sessions:
                return "ℹ️ *No active tmux sessions found on host.*"
            lines = [
                "### 🖥️ Active Host Tmux Sessions\n",
                "| Session | Windows | Attached | Active Window |",
                "| :--- | :--- | :--- | :--- |",
            ]
            for s in sessions:
                att = "✅ Yes" if s.attached else "No"
                win = s.active_window or "bash"
                lines.append(f"| `{s.name}` | {s.windows} | {att} | {win} |")
            return "\n".join(lines)

        if cmd == "new":
            if not args:
                return "❌ *Usage: `/new <session_name> [start_dir] [command]`*"
            session_name = args[0]
            start_dir = args[1] if len(args) > 1 else None
            command = " ".join(args[2:]) if len(args) > 2 else None
            try:
                await self.driver.new_session(session_name, start_dir=start_dir, command=command)
                msg = f"✅ Session `{session_name}` created successfully."
                if start_dir:
                    msg += f" Directory: `{start_dir}`."
                if command:
                    msg += f" Command: `{command}`."
                return msg
            except Exception as ex:
                return f"❌ Failed to create session `{session_name}`: {ex}"

        if cmd == "kill":
            if not args:
                return "❌ *Usage: `/kill <session_name>`*"
            session_name = args[0]
            try:
                await self.driver.kill_session(session_name)
                return f"✅ Session `{session_name}` killed."
            except Exception as ex:
                return f"❌ Failed to kill session `{session_name}`: {ex}"

        if cmd == "keys":
            if not args:
                return "❌ *Usage: `/keys <key_combination>` (e.g. `C-c`, `Escape`, `Enter`)*"
            # Note: /keys will be handled in session context
            return f"Special keys command received: `{' '.join(args)}`"

        return f"❓ Unknown slash command `/{cmd}`. Type `/help` for available commands."

    def calculate_delta(self, baseline_text: str, current_text: str) -> str:
        """Extract only new lines appended to terminal since baseline."""
        cleaned_base = clean_terminal_output(baseline_text)
        cleaned_curr = clean_terminal_output(current_text)

        base_lines = cleaned_base.splitlines()
        curr_lines = cleaned_curr.splitlines()

        if not base_lines:
            return cleaned_curr

        # Find suffix match
        match_idx = 0
        max_search = min(len(base_lines), 20)
        for i in range(1, max_search + 1):
            if curr_lines[:i] == base_lines[-i:]:
                match_idx = i

        if match_idx > 0 and len(curr_lines) >= match_idx:
            new_lines = curr_lines[match_idx:]
            return "\n".join(new_lines)

        # Fallback: if curr_lines starts with base_lines
        if len(curr_lines) >= len(base_lines) and curr_lines[: len(base_lines)] == base_lines:
            return "\n".join(curr_lines[len(base_lines) :])

        # If terminal was cleared or redrawn, return current text
        return cleaned_curr

    async def stream_command(
        self,
        session_name: str,
        user_message: str,
        stream_id: str = "chatcmpl-tmux",
    ) -> AsyncGenerator[str, None]:
        """Stream terminal delta execution as OpenAI-compatible SSE events."""
        created_ts = int(time.time())
        model_id = f"tmux:{session_name}"

        # 1. Check for slash commands
        parsed = self.parse_slash_command(user_message)
        if parsed:
            cmd, args = parsed
            if cmd == "keys" and args:
                key_combo = args[0]
                try:
                    await self.driver.send_keys(session_name, key_combo, enter=False)
                    response_text = f"Sent key `{key_combo}` to session `{session_name}`."
                except Exception as ex:
                    response_text = f"❌ Failed to send key `{key_combo}`: {ex}"
            else:
                response_text = await self.handle_slash_command(cmd, args)

            # Emit single chunk then DONE
            chunk = ChatCompletionChunk(
                id=stream_id,
                created=created_ts,
                model=model_id,
                choices=[
                    ChatCompletionChunkChoice(
                        delta=ChatDelta(role="assistant", content=response_text),
                        finish_reason=None,
                    )
                ],
            )
            yield f"data: {chunk.model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"
            return

        # 2. Verify target session exists
        if not await self.driver.has_session(session_name):
            err_msg = (
                f"❌ Tmux session `{session_name}` does not exist.\n\n"
                f"Use `/new {session_name}` to spawn it or `/list` to view available sessions."
            )
            chunk = ChatCompletionChunk(
                id=stream_id,
                created=created_ts,
                model=model_id,
                choices=[
                    ChatCompletionChunkChoice(
                        delta=ChatDelta(role="assistant", content=err_msg),
                        finish_reason="stop",
                    )
                ],
            )
            yield f"data: {chunk.model_dump_json()}\n\n"
            yield "data: [DONE]\n\n"
            return

        # 3. Capture baseline snapshot before injecting input
        try:
            baseline = await self.driver.capture_pane(
                session_name, lines=self.config.max_scrollback_lines
            )
        except Exception as ex:
            baseline = ""
            logger.warning(f"Failed to capture baseline for {session_name}: {ex}")

        # 4. Inject user input into tmux pane
        await self.driver.send_keys(session_name, user_message, enter=True)

        # 5. Polling & Streaming loop
        start_time = time.monotonic()
        last_change_time = start_time
        last_emitted_delta = ""
        has_emitted_any = False

        while True:
            await asyncio.sleep(self.config.poll_interval_sec)
            now = time.monotonic()

            try:
                curr_snapshot = await self.driver.capture_pane(
                    session_name, lines=self.config.max_scrollback_lines
                )
            except Exception as ex:
                logger.error(f"Error capturing pane during stream: {ex}")
                break

            delta = self.calculate_delta(baseline, curr_snapshot)

            if delta != last_emitted_delta:
                # We have new output!
                last_change_time = now
                new_token_text = (
                    delta[len(last_emitted_delta) :]
                    if delta.startswith(last_emitted_delta)
                    else delta
                )

                if new_token_text:
                    chunk = ChatCompletionChunk(
                        id=stream_id,
                        created=created_ts,
                        model=model_id,
                        choices=[
                            ChatCompletionChunkChoice(
                                delta=ChatDelta(content=new_token_text),
                                finish_reason=None,
                            )
                        ],
                    )
                    yield f"data: {chunk.model_dump_json()}\n\n"
                    last_emitted_delta = delta
                    has_emitted_any = True

            # Quiescence detection: output has stopped changing for quiescence_timeout_sec
            quiescent_duration = now - last_change_time
            total_duration = now - start_time

            if has_emitted_any and quiescent_duration >= self.config.quiescence_timeout_sec:
                logger.debug(f"Stream quiescence reached after {quiescent_duration:.2f}s silence")
                break

            # Hard safety timeout
            if total_duration >= self.config.stream_timeout_sec:
                logger.warning(f"Stream safety timeout reached ({self.config.stream_timeout_sec}s)")
                break

            # If no output at all for 3 seconds, break
            if not has_emitted_any and total_duration >= 3.0:
                break

        # Send final completion finish chunk
        finish_chunk = ChatCompletionChunk(
            id=stream_id,
            created=created_ts,
            model=model_id,
            choices=[
                ChatCompletionChunkChoice(
                    delta=ChatDelta(),
                    finish_reason="stop",
                )
            ],
        )
        yield f"data: {finish_chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    async def execute_command_non_streaming(self, session_name: str, user_message: str) -> str:
        """Execute command and wait for output stabilization, returning full text."""
        chunks: list[str] = []
        async for sse_line in self.stream_command(session_name, user_message):
            if sse_line.startswith("data: ") and not sse_line.startswith("data: [DONE]"):
                try:
                    payload = json.loads(sse_line[6:].strip())
                    chunk = ChatCompletionChunk.model_validate(payload)
                    for choice in chunk.choices:
                        if choice.delta.content:
                            chunks.append(choice.delta.content)
                except Exception:
                    pass
        return "".join(chunks)
