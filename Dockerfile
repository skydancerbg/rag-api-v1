# /opt/rag-api/Dockerfile v1.1.3

FROM python:3.11-slim

# Install system dependencies for PDF, Word, PPT parsing + OCR
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      build-essential poppler-utils tesseract-ocr libgl1 libglib2.0-0 libsm6 libxrender1 wget && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY rag-api/ ./rag_api/

# Set environment variables (default values)
ENV PYTHONUNBUFFERED=1

# Uvicorn default port
EXPOSE 5005

# Start FastAPI app
CMD ["uvicorn", "rag_api.main:app", "--host", "0.0.0.0", "--port", "5005"]
