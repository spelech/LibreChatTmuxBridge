"""
Domain and API data models for LibreChatTmuxBridge.
"""

from typing import Literal

from pydantic import BaseModel, Field

# ==========================================
# Tmux Domain Models
# ==========================================


class TmuxSession(BaseModel):
    """Represents an active tmux session on the host."""

    name: str = Field(..., description="Unique tmux session identifier")
    windows: int = Field(default=1, description="Number of active windows")
    created: int | None = Field(default=None, description="Unix timestamp of creation")
    attached: bool = Field(default=False, description="Whether currently attached via terminal/SSH")
    active_window: str | None = Field(
        default=None, description="Name of the currently active window"
    )


class CommandResult(BaseModel):
    """Execution output of a tmux or system command."""

    command: str = Field(..., description="Executed command string")
    stdout: str = Field(default="", description="Standard output")
    stderr: str = Field(default="", description="Standard error")
    exit_code: int = Field(default=0, description="Process exit code")
    success: bool = Field(default=True, description="Whether exit code is 0")


# ==========================================
# OpenAI API Compatibility Models
# ==========================================


class ChatMessage(BaseModel):
    """Single chat message in an OpenAI conversation."""

    role: Literal["system", "user", "assistant", "tool"] = Field(
        ..., description="Message author role"
    )
    content: str = Field(default="", description="Message text content")
    name: str | None = Field(default=None, description="Optional author display name")


class ChatCompletionRequest(BaseModel):
    """Standard OpenAI /v1/chat/completions payload."""

    model: str = Field(..., description="Target model ID (e.g. 'tmux:agy-work' or 'tmux:new')")
    messages: list[ChatMessage] = Field(..., description="List of previous conversation turns")
    stream: bool = Field(default=False, description="Whether to stream response tokens via SSE")
    temperature: float | None = Field(
        default=None, description="Optional temperature parameter (ignored)"
    )
    max_tokens: int | None = Field(default=None, description="Optional max tokens limit (ignored)")


class ModelObject(BaseModel):
    """Single OpenAI model descriptor."""

    id: str = Field(..., description="Model identifier (e.g. 'tmux:agy-work')")
    object: Literal["model"] = "model"
    created: int = Field(default=1700000000, description="Unix timestamp")
    owned_by: str = Field(default="tmux-bridge", description="Owner identifier")


class ModelList(BaseModel):
    """OpenAI GET /v1/models response payload."""

    object: Literal["list"] = "list"
    data: list[ModelObject] = Field(default_factory=list, description="Available models")


class ChatDelta(BaseModel):
    """Streaming delta chunk in a chat completion."""

    role: str | None = None
    content: str | None = None


class ChatCompletionChunkChoice(BaseModel):
    """Choice element inside an SSE completion chunk."""

    index: int = 0
    delta: ChatDelta = Field(default_factory=ChatDelta)
    finish_reason: str | None = None


class ChatCompletionChunk(BaseModel):
    """Top-level SSE chunk emitted during streaming completions."""

    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: list[ChatCompletionChunkChoice] = Field(default_factory=list)


class ChatCompletionChoice(BaseModel):
    """Choice element inside a non-streaming completion response."""

    index: int = 0
    message: ChatMessage
    finish_reason: str = "stop"


class Usage(BaseModel):
    """Token usage counters (0 tokens used for local bridge)."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponse(BaseModel):
    """Non-streaming OpenAI /v1/chat/completions response."""

    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice] = Field(default_factory=list)
    usage: Usage = Field(default_factory=Usage)


# ==========================================
# Health & Status Models
# ==========================================


class HealthResponse(BaseModel):
    """Health check status response."""

    status: str = "healthy"
    version: str = "0.1.0"
    uptime_seconds: float
    active_sessions: int
