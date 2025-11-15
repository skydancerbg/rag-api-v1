# /opt/rag-api/Dockerfile v1.1.4
FROM python:3.11-slim

# System dependencies for PDF/Word/PPT parsing + OCR fallback
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential poppler-utils tesseract-ocr libgl1 libglib2.0-0 libsm6 libxrender1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY rag-api/ ./rag_api/

# Expose API port
EXPOSE 5005

# Start FastAPI
CMD ["uvicorn", "rag_api.main:app", "--host", "0.0.0.0", "--port", "5005"]
