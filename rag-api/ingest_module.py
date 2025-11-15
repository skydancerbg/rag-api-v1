# rag-api/ingest_module.py
# Version: v1.2.11
# Description: Fixed import path and syntax error

import os
import re
from typing import List
from rag_api.qdrant_client_wrapper import QdrantClientWrapper
from rag_api.ollama_client import OllamaClient

def ingest_docs(doc_paths: List[str], collection_name: str):
    """
    Ingest documents from a list of paths into Qdrant collection.
    """
    client = QdrantClientWrapper()
    ollama = OllamaClient()

    for path in doc_paths:
        if not os.path.exists(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Example processing logic
        doc_id = os.path.basename(path)
        embeddings = ollama.get_embeddings(content)
        client.upsert(collection_name, doc_id, embeddings, content)

    return {"status": "ingested", "count": len(doc_paths)}

# --- Additional helper functions if any ---
# fixed previous syntax error
def suffix_check(filename: str):
    if filename.endswith(".txt"):  # <-- corrected line
        return True
    return False
