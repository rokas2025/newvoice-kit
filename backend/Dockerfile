# syntax=docker/dockerfile:1

# Use Python 3.13 slim image
ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION}-slim-bookworm AS base

# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Create a non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Install build dependencies for Python packages with native extensions
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
  && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml ./

# Install dependencies using pip
RUN pip install --no-cache-dir -e .

# Copy all application files
COPY . .

# Change ownership to non-privileged user
RUN chown -R appuser:appuser /app

# Switch to non-privileged user
USER appuser

# Pre-download ML models and files
RUN python src/agent.py download-files

# Run the agent
CMD ["python", "src/agent.py", "start"]
