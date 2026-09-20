FROM python:3.12-slim

# Install system dependencies including tmux
RUN apt-get update && apt-get install -y --no-install-recommends \
    tmux \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency manifests
COPY pyproject.toml README.md /app/

# Install dependencies
RUN uv sync --no-dev

# Copy source tree
COPY src/ /app/src/

# Expose port
EXPOSE 8035

# Start daemon
CMD ["uv", "run", "librechat-tmux-bridge", "start", "--host", "0.0.0.0", "--port", "8035"]
