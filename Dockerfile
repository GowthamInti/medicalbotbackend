# Stage 1: Pull from the unstructured image

# Stage 2: Your base Python image
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (only if not already in base image)
RUN apt-get update && apt-get install -y \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Build arguments for environment variables
ARG GROQ_API_KEY
ARG REDIS_URL
ARG SECRET_KEY
ARG DEFAULT_ADMIN_USERNAME=admin
ARG DEFAULT_ADMIN_PASSWORD=admin123
ARG LLM_PROVIDER=chatgroq
ARG GROQ_BASE_URL=https://api.groq.com/openai/v1
ARG GROQ_MODEL_NAME=llama3-8b-8192
ARG TEMPERATURE=0.7
ARG MAX_TOKENS=1024
ARG MEMORY_TTL_SECONDS=3600
ARG MAX_CACHE_SIZE=1000
ARG ACCESS_TOKEN_EXPIRE_MINUTES=60

# Set environment variables from build args
ENV GROQ_API_KEY=${GROQ_API_KEY}
ENV REDIS_URL=${REDIS_URL}
ENV SECRET_KEY=${SECRET_KEY}
ENV DEFAULT_ADMIN_USERNAME=${DEFAULT_ADMIN_USERNAME}
ENV DEFAULT_ADMIN_PASSWORD=${DEFAULT_ADMIN_PASSWORD}
ENV LLM_PROVIDER=${LLM_PROVIDER}
ENV GROQ_BASE_URL=${GROQ_BASE_URL}
ENV GROQ_MODEL_NAME=${GROQ_MODEL_NAME}
ENV TEMPERATURE=${TEMPERATURE}
ENV MAX_TOKENS=${MAX_TOKENS}
ENV MEMORY_TTL_SECONDS=${MEMORY_TTL_SECONDS}
ENV MAX_CACHE_SIZE=${MAX_CACHE_SIZE}
ENV ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
