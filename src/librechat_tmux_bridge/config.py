"""
Configuration settings for LibreChatTmuxBridge using Pydantic Settings.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BridgeConfig(BaseSettings):
    """Bridge runtime settings loaded from environment or defaults."""

    model_config = SettingsConfigDict(env_prefix="TMUX_BRIDGE_", env_file=".env", extra="ignore")

    host: str = Field(default="0.0.0.0", description="Host address to bind to")
    port: int = Field(default=8035, description="Port to listen on (Pipeline Pattern 8035)")
    api_key: str = Field(
        default="sk-tmux", description="Bearer API key for LibreChat custom endpoint"
    )
    tmux_bin: str = Field(default="tmux", description="Path or command name for tmux binary")
    tmux_socket: str | None = Field(
        default=None, description="Optional custom tmux socket path (-S)"
    )
    max_scrollback_lines: int = Field(
        default=200, description="Maximum lines to capture from pane history"
    )
    poll_interval_sec: float = Field(
        default=0.1, description="Polling interval for terminal delta detection"
    )
    quiescence_timeout_sec: float = Field(
        default=0.8, description="Silence duration after output before stream ends"
    )
    stream_timeout_sec: float = Field(
        default=30.0, description="Hard timeout for terminal stream execution"
    )
    log_level: str = Field(default="INFO", description="Application logging level")
    cors_origins: list[str] = Field(default=["*"], description="Allowed CORS origins")
    mcp_enabled: bool = Field(
        default=True, description="Enable Model Context Protocol (MCP) server"
    )


# Global settings singleton
settings = BridgeConfig()
