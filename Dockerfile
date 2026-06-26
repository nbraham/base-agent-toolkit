# Base Agent Toolkit — Docker Image

FROM python:3.12-slim AS base

# Metadata
LABEL maintainer="nbraham"
LABEL description="Base Agent Toolkit — Python SDK for AI agents on Base L2"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy source
COPY src/ src/
COPY examples/ examples/

# Default command
ENTRYPOINT ["python", "-m", "base_agent_toolkit.cli.main"]
CMD ["info"]

# ---
# Development stage
FROM base AS dev

COPY tests/ tests/
COPY Makefile .

RUN pip install --no-cache-dir -e ".[dev]"

CMD ["pytest", "-v"]
