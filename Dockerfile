# Dockerfile v1
FROM python:3.11-slim

# Install system deps needed for PDF/Word/PPT parsing + OCR fallback
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential poppler-utils tesseract-ocr libgl1 libglib2.0-0 libsm6 libxrender1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rag-api/ ./rag_api/

ENV PYTHONUNBUFFERED=1

EXPOSE 5005

CMD ["uvicorn", "rag_api.main:app", "--host", "0.0.0.0", "--port", "5005"]
