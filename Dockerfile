# Talos MCP Server Dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

# Install dependencies
RUN uv sync --frozen --no-dev

# Create non-root user
RUN useradd -m -u 1000 talos && \
    chown -R talos:talos /app

USER talos

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Default command
CMD ["uv", "run", "talos-mcp-server"]
