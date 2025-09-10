# Multi-stage Dockerfile for LangGraph + Obsidian Integration
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install UV for fast Python package management
RUN pip install uv

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /data/vector /data/graph /data/checkpoints

# Development stage
FROM base as development
ENV ENVIRONMENT=development
ENV DEBUG=true
EXPOSE 8000
CMD ["python", "-m", "api_gateway.main"]

# Production stage
FROM base as production
ENV ENVIRONMENT=production
ENV DEBUG=false
EXPOSE 8000
CMD ["python", "-m", "api_gateway.main"]