# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY backend /app/backend
COPY data /app/data

# Expose port
EXPOSE 8000

# Env
ENV DATA_DIR=/app/data

# Start
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]
