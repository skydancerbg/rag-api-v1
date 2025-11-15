# Version: v1.2.2
# Description: Fix GHCR build paths and add system dependencies for Ollama, PDF, PPTX, HTML parsing

FROM python:3.11-slim

# Install system dependencies required by pypdf2, python-pptx, bs4, lxml, cryptography
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

# Copy project files with correct paths for GitHub Actions
COPY rag-api-v1/rag-api /app/rag_api
COPY rag-api-v1/config /app/config
COPY rag-api-v1/docs /app/docs
COPY rag-api-v1/requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Environment variables (keep same as previous)
ENV DOC_PATH=/app/docs
ENV QDRANT_URL=http://10.100.10.2:6333
ENV COLLECTION_NAME=documents
ENV VECTOR_DIM=384
ENV OLLAMA_URL=http://10.10.10.5:11434
ENV OLLAMA_MODEL=gpt-oss:20b
ENV CHUNK_WORDS=500

# Start API
CMD ["uvicorn", "rag_api.main:app", "--host", "0.0.0.0", "--port", "5005"]
