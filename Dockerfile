# Multi-stage Dockerfile for Knotts Accounting Backend

# Base stage with Python and system dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Africa/Johannesburg

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    wget \
    git \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgomp1 \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Create app directory
WORKDIR /app

# Development stage
FROM base as development

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies including dev dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/temp

# Set permissions
RUN chmod -R 755 /app

# Expose port
EXPOSE 8000

# Development command with hot reload
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Testing stage
FROM development as testing

# Run linting
RUN flake8 src/ || true
RUN mypy src/ || true

# Run tests with coverage
RUN pytest tests/ --cov=src --cov-report=term-missing || true

# Production stage
FROM base as production

# Copy requirements
COPY requirements.txt ./

# Install production dependencies only
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy application code from development stage
COPY --from=development /app/src ./src
COPY --from=development /app/alembic ./alembic
COPY --from=development /app/alembic.ini ./alembic.ini

# Create non-root user
RUN useradd -m -u 1000 knotts && \
    mkdir -p /app/logs /app/uploads /app/temp && \
    chown -R knotts:knotts /app

# Switch to non-root user
USER knotts

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command with gunicorn
CMD ["gunicorn", "src.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--access-logfile", "/app/logs/access.log", "--error-logfile", "/app/logs/error.log"]