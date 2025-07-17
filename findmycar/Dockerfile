FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    sqlite3 \
    curl \
    wget \
    gnupg \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy application code
COPY . .

# Create data directory for database persistence
RUN mkdir -p /app/data

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash cargpt && \
    chown -R cargpt:cargpt /app
USER cargpt

# Chrome not needed for basic deployment

# Expose port 8000 (updated from 3100)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]