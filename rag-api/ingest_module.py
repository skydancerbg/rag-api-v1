# rag-api v1.1.5 — ingest_module.py
# Purpose: minimal, reliable ingestion and listing functions so the API is operational.
# - deterministic UUID5 point ids based on file path to avoid duplicates
# - uses 384-dim zero vectors (placeholder) so Qdrant upserts succeed immediately
# - functions: ingest_docs(), list_docs(), ask_query()
# Note: Replace vector generation with real embeddings later.

import os
import uuid
import time
import json
from pathlib import Path
import requests

DOC_PATH = os.getenv("DOC_PATH", "/mnt/ai-rag-files")
QDRANT_URL = os.getenv("QDRANT_URL", "http://10.100.10.2:6333")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documents")
VECTOR_DIM = int(os.getenv("VECTOR_DIM", "384"))

# helper: deterministic uuid5 from path
UUID_NAMESPACE = uuid.UUID("12345678-1234-5678-1234-567812345678")

def _file_id(path: str):
    """Deterministic UUID from file path (string)."""
    return str(uuid.uuid5(UUID_NAMESPACE, path))

def _zero_vector():
    return [0.0] * VECTOR_DIM

def _qdrant_upsert_point(point_id: str, vector, payload: dict):
    url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points"
    body = {"points": [{"id": point_id, "vector": vector, "payload": payload}]}
    resp = requests.put(url, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()

def _ensure_collection():
    # Try to create collection if missing (384 dim by default)
    url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}"
    resp = requests.get(url, timeout=5)
    if resp.status_code == 200:
        return True
    # create
    body = {
        "vectors": {"size": VECTOR_DIM, "distance": "Cosine"},
    }
    resp = requests.put(f"{QDRANT_URL}/collections/{COLLECTION_NAME}", json=body, timeout=10)
    resp.raise_for_status()
    return True

def ingest_docs() -> list:
    """
    Scan DOC_PATH for files and upsert them into Qdrant.
    Returns list of ingested file names (new or updated).
    Deterministic IDs prevent duplicates.
    """
    _ensure_collection()
    docs = []
    p = Path(DOC_PATH)
    if not p.exists():
        return {"error": f"documents path not found: {DOC_PATH}"}
    for f in p.rglob("*"):
        if f.is_file():
            try:
                rel = str(f.resolve())
                pid = _file_id(rel)
                stat = f.stat()
                payload = {
                    "path": rel,
                    "name": f.name,
                    "size": stat.st_size,
                    "mtime": int(stat.st_mtime),
                }
                # Use zero vector placeholder — replace with embeddings later
                vec = _zero_vector()
                _qdrant_upsert_point(pid, vec, payload)
                docs.append(rel)
            except Exception as e:
                # do not abort whole ingestion on single file error
                print("ingest_docs: error for", str(f), repr(e))
                continue
    return docs

def list_docs(limit: int = 100):
    """
    Return a list of payloads from Qdrant (up to limit).
    """
    url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points/scroll"
    body = {"limit": limit, "with_vector": False, "with_payload": True}
    resp = requests.post(url, json=body, timeout=30)
    if resp.status_code != 200:
        return {"error": f"qdrant scroll failed: {resp.status_code}"}
    data = resp.json()
    # data.result.points maybe in v1.15+; support both shapes
    points = data.get("result", {}).get("points") or data.get("result") or data.get("points") or data
    # normalize safe return
    items = []
    # If response is list-like
    if isinstance(points, list):
        for p in points:
            items.append({"id": p.get("id"), "payload": p.get("payload")})
    else:
        # fallback: try data["result"]["points"]
        res_points = data.get("result", {}).get("points", [])
        for p in res_points:
            items.append({"id": p.get("id"), "payload": p.get("payload")})
    return items

def ask_query(query: str):
    """
    Minimal placeholder for ask: returns top-K text matches from Qdrant payloads.
    This does NOT call Ollama embeddings — it's a simple nearest-by-payload fallback.
    Replace with proper embedding+LLM prompt chain later.
    """
    # We will return simple hits by scanning payloads for query substring in filename.
    hits = []
    all_docs = list_docs(limit=500)
    q = query.lower()
    for item in all_docs:
        payload = item.get("payload") or {}
        name = (payload.get("name") or "").lower()
        path = (payload.get("path") or "").lower()
        if q in name or q in path:
            hits.append({"id": item.get("id"), "payload": payload})
    # If no hits, return a friendly message
    if not hits:
        return {"answer": "No local documents matched your query yet."}
    return {"hits": hits}
