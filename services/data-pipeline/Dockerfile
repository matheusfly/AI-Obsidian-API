FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and UV
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with UV (ultra-fast)
RUN uv pip install --system --no-cache -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create data directory
RUN mkdir -p ./data/chroma

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8003

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8003/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8003"]
