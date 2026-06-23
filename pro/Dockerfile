# Multi-stage build for ETL Pipeline
FROM python:3.11-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY etl_pipeline.py .
COPY scheduler.py .
COPY monitor.py .
COPY config.json .
COPY airflow_dag.py .

# Create logs directory
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_DIR=/app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import psycopg2; psycopg2.connect('dbname=postgres user=postgres host=postgres_source')" || exit 1

# Default command: run ETL pipeline
CMD ["python", "etl_pipeline.py", "config.json"]
