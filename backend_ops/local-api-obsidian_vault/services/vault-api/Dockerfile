# syntax=docker/dockerfile:1.7
FROM python:3.11-slim

# Install UV (fast Python package manager) and build essentials
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Make sure uv is on PATH
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Install Python dependencies with uv (fast, cached)
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8080

# Use `uv run` to execute without syncing (deps already installed)
CMD ["uv", "run", "--no-sync", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
