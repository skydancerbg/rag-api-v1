# Version: v1.2.0
# Description: Multi-format ingestion, chunking, Ollama embeddings, deterministic UUIDs, manual API endpoint support

import os
import uuid
import json
import logging
from pathlib import Path
from typing import List

import requests
import numpy as np

# Optional document parsing libraries
try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None

try:
    import pptx
except ImportError:
    pptx = None

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Configuration via environment variables
DOC_PATH = os.environ.get("DOC_PATH", "/mnt/ai-rag-files")
QDRANT_URL = os.environ.get("QDRANT_URL", "http://10.100.10.2:6333")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "documents")
VECTOR_DIM = int(os.environ.get("VECTOR_DIM", "384"))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://10.10.10.5:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gpt-oss:20b")
CHUNK_WORDS = int(os.environ.get("CHUNK_WORDS", "500"))
INGEST_NAMESPACE_UUID = uuid.UUID(os.environ.get("INGEST_NAMESPACE_UUID", uuid.uuid4().hex))

# Initialize Qdrant client
qdrant = QdrantClient(url=QDRANT_URL)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------- Utility Functions ----------

def deterministic_id(path: str, chunk_idx: int) -> str:
    """Create deterministic UUIDv5 for a document chunk"""
    name = f"{path}-{chunk_idx}"
    return str(uuid.uuid5(INGEST_NAMESPACE_UUID, name))


def chunk_text(text: str, chunk_size: int = CHUNK_WORDS) -> List[str]:
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]


def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    try:
        if suffi
