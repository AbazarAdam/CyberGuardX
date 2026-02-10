# =============================================================================
# CyberGuardX — Production Dockerfile
# =============================================================================
# Multi-stage build for optimized production image

FROM python:3.11-slim as builder

# Metadata
LABEL maintainer="CyberGuardX Team"
LABEL version="2.0.0"
LABEL description="CyberGuardX - Intelligent Web Security Assessment Platform"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# Production stage
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Create non-root user for security
RUN useradd -m -u 1000 cyberguard && \
    mkdir -p /app /app/logs /app/data /app/models && \
    chown -R cyberguard:cyberguard /app

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=cyberguard:cyberguard backend/ ./backend/
COPY --chown=cyberguard:cyberguard requirements.txt .

# Copy data and models (if they exist)
COPY --chown=cyberguard:cyberguard data/ ./data/ 2>/dev/null || true
COPY --chown=cyberguard:cyberguard models/ ./models/ 2>/dev/null || true

# Switch to non-root user
USER cyberguard

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/', timeout=5)" || exit 1

# Run application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
