# =============================================================================
# M537 Voice Gateway - Multi-Stage Docker Build
# Optimized for small image size and fast builds
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies
# -----------------------------------------------------------------------------
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Production - Minimal runtime image
# -----------------------------------------------------------------------------
FROM python:3.11-slim as production

# Labels for container metadata
LABEL maintainer="LIGHT HOPE <support@lighthope.ai>"
LABEL version="1.0.0"
LABEL description="M537 Voice Gateway - Natural language server access"
LABEL org.opencontainers.image.source="https://github.com/lighthope-ai/m537-voice-gateway"

# Create non-root user for security
RUN groupadd -r m537 && useradd -r -g m537 m537

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    procps \
    iproute2 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=m537:m537 backend/ ./backend/
COPY --chown=m537:m537 frontend/ ./frontend/

# Create necessary directories
RUN mkdir -p /app/logs && chown -R m537:m537 /app

# Set environment variables
ENV PYTHONPATH=/app/backend
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5537

# Switch to non-root user
USER m537

# Set working directory to backend
WORKDIR /app/backend

# Expose port
EXPOSE 5537

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5537/health || exit 1

# Run the application with optimized settings
CMD ["python", "-m", "uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "5537", \
     "--workers", "2", \
     "--loop", "uvloop", \
     "--http", "httptools", \
     "--no-access-log"]

# -----------------------------------------------------------------------------
# Stage 3: Development - Full development environment
# -----------------------------------------------------------------------------
FROM production as development

USER root

# Install development tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    vim \
    htop \
    && rm -rf /var/lib/apt/lists/*

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    ruff \
    mypy

USER m537

# Development command with hot reload
CMD ["python", "-m", "uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "5537", \
     "--reload"]
