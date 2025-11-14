# embeddings.py v1
import os
from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
_model = SentenceTransformer(MODEL_NAME)

def embed_text(text_or_list):
    """
    Accepts a string or list[str], returns list of vectors (lists of floats).
    """
    if isinstance(text_or_list, str):
        texts = [text_or_list]
    else:
        texts = text_or_list
    return _model.encode(texts).tolist()
