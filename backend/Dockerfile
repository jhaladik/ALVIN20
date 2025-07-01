# backend/Dockerfile - ALVIN Backend Production Image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production \
    FLASK_CONFIG=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libpq-dev \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r alvin && useradd -r -g alvin alvin

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads logs exports backups \
    && chown -R alvin:alvin /app

# Switch to non-root user
USER alvin

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--worker-class", "eventlet", "--worker-connections", "1000", "--timeout", "30", "--keepalive", "2", "--max-requests", "1000", "--max-requests-jitter", "100", "run:app"]