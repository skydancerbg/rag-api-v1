# ingest_module.py v1
from pathlib import Path
import os
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams
from .embeddings import embed_text
from .utils import extract_text
from typing import List

QDRANT_URL = os.getenv("QDRANT_URL", "http://10.100.10.2:6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documents")
DOC_PATH = os.getenv("DOC_PATH", "/mnt/ai-rag-files")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))

client = QdrantClient(url=QDRANT_URL)

def ensure_collection(dim=384):
    cols = client.get_collections().collections
    names = [c.name for c in cols]
    if COLLECTION_NAME not in names:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=dim, distance="Cosine")
        )

def chunk_text(text: str, size: int = CHUNK_SIZE) -> List[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    for i in range(0, len(words), size):
        chunks.append(" ".join(words[i:i+size]))
    return chunks

def upsert_points(points):
    # qdrant-client will accept list of dicts with id, vector, payload
    client.upsert(collection_name=COLLECTION_NAME, points=points)

def ingest_documents():
    ensure_collection()
    base = Path(DOC_PATH)
    files = list(base.rglob("*"))
    print(f"[ingest] found {len(files)} entries under {DOC_PATH}")
    ingested_files = 0
    for f in files:
        if not f.is_file():
            continue
        try:
            text = extract_text(f)
            if not text or not text.strip():
                continue
            chunks = chunk_text(text)
            vectors = embed_text(chunks)
            points = []
            for idx, (chunk, vector) in enumerate(zip(chunks, vectors)):
                # deterministic ID per file + chunk
                point_id = f"{uuid.uuid5(uuid.NAMESPACE_URL, str(f))}-{idx}"
                payload = {"text": chunk, "source_file": str(f.name), "chunk_id": idx}
                points.append({"id": point_id, "vector": vector, "payload": payload})
            # upload in batch
            upsert_points(points)
            ingested_files += 1
            print(f"[ingest] ingested {f.name} ({len(chunks)} chunks)")
        except Exception as e:
            print(f"[ingest] failed {f.name}: {e}")
    print(f"[ingest] complete. files ingested: {ingested_files}")
