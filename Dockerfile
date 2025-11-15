# rag-api v1.1.5 — Dockerfile (only changed PYTHONPATH)
FROM python:3.11-slim

# rag-api v1.1.5: updated PYTHONPATH so mounted /app/rag_api is resolvable as package rag_api

# Install system deps
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential poppler-utils tesseract-ocr libgl1 libglib2.0-0 libsm6 libxrender1 wget && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# keep existing copy line
COPY rag-api/ ./rag_api/

# ensure python can import rag_api when /app/rag_api is mounted
ENV PYTHONPATH=/app

EXPOSE 5005

CMD ["uvicorn", "rag_api.main:app", "--host", "0.0.0.0", "--port", "5005"]
