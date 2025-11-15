# /opt/rag-api/rag-api/ingest_module.py
# Version: v1.2.10
# Description: RAG ingestion module for rag-api; fixed SyntaxError at line 71

import os
import time
import logging
from typing import List
from pathlib import Path
from fastapi import HTTPException

# Example: Qdrant client import
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Load environment variables
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documents")
DOC_PATH = os.getenv("DOC_PATH", "/mnt/ai-rag-files")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
TOP_K = int(os.getenv("TOP_K", 5))

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Qdrant client
qdrant_client = QdrantClient(url=QDRANT_URL)


def list_files(path: str) -> List[Path]:
    """
    List all document files in the specified path.
    """
    doc_dir = Path(path)
    if not doc_dir.exists():
        raise HTTPException(status_code=404, detail=f"Document path {path} not found")
    return [f for f in doc_dir.iterdir() if f.is_file()]


def ingest_docs():
    """
    Main ingestion logic: read files from DOC_PATH and index into Qdrant.
    """
    logger.info(f"Starting ingestion from {DOC_PATH} into collection '{COLLECTION_NAME}'")
    files = list_files(DOC_PATH)
    allowed_suffixes = [".txt", ".pdf", ".md"]  # adjust based on your documents

    for file in files:
        suffix = file.suffix.lower()
        # --- FIXED SYNTAX ERROR ---
        if suffix in allowed_suffixes:
            logger.info(f"Processing file: {file.name}")
            try:
                text = file.read_text(encoding="utf-8")
                # Split text into chunks
                chunks = [text[i:i+CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
                for chunk in chunks:
                    point = PointStruct(id=int(time.time() * 1000000), vector=hash(chunk) % 1000000, payload={"text": chunk})
                    qdrant_client.upsert(collection_name=COLLECTION_NAME, points=[point])
            except Exception as e:
                logger.error(f"Error processing file {file.name}: {e}")
        else:
            logger.warning(f"Skipping unsupported file type: {file.name}")

    logger.info("Ingestion completed successfully.")
    return {"status": "success", "files_indexed": len(files)}


if __name__ == "__main__":
    # Standalone run
    ingest_docs()
