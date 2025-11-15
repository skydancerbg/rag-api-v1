# Dockerfile v1.2.7
# Description: Remove non-existent /docs COPY to fix GHCR build. Base: v1.1.5

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libpq-dev \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy project files from repo root (keep exact paths from v1.1.5)
COPY rag-api /app/rag_api
COPY config /app/config
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Environment variables (from v1.1.5)
ENV DOC_PATH=/mnt/ai-rag-files
ENV QDRANT_URL=http://10.100.10.2:6333
ENV COLLECTION_NAME=documents
ENV VECTOR_DIM=384
ENV OLLAMA_URL=http://10.10.10.5:11434
ENV OLLAMA_MODEL=gpt-oss:20b
ENV CHUNK_WORDS=500

# Start FastAPI
CMD ["uvicorn", "rag_api.main:app", "--host", "0.0.0.0", "--port", "5005"]
