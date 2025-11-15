# Version: v1.2.0
# Description: Update dependencies for Ollama embeddings and multi-format ingestion

FROM python:3.11-slim

WORKDIR /app

# Copy code
COPY rag-api /app/rag_api
COPY config /app/config
COPY docs /app/docs
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Environment variables
ENV DOC_PATH=/app/docs
ENV QDRANT_URL=http://10.100.10.2:6333
ENV COLLECTION_NAME=documents
ENV VECTOR_DIM=384
ENV OLLAMA_URL=http://10.10.10.5:11434
ENV OLLAMA_MODEL=gpt-oss:20b
ENV CHUNK_WORDS=500

# Start API
CMD ["uvicorn", "rag_api.main:app", "--host", "0.0.0.0", "--port", "5005"]
