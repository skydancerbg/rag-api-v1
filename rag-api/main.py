# main.py v1
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sse_starlette.sse import EventSourceResponse
from .ingest_module import ingest_documents, client, COLLECTION_NAME
from .embeddings import embed_text
import requests
import json

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://10.10.10.5:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gpt-oss:20b")
TOP_K = int(os.getenv("TOP_K", 5))
INGEST_INTERVAL_MIN = int(os.getenv("INGEST_INTERVAL_MIN", 10))

app = FastAPI(title="RAG API")

# CORS — restrict if desired (OpenWebUI IP: 10.100.10.106)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to ["http://10.100.10.106:8080"] for production
    allow_methods=["*"],
    allow_headers=["*"],
)

# Scheduler: periodic ingestion
scheduler = AsyncIOScheduler()
scheduler.add_job(ingest_documents, "interval", minutes=INGEST_INTERVAL_MIN)
scheduler.start()

@app.on_event("startup")
async def startup_event():
    # initial ingestion (non-blocking)
    ingest_documents()

@app.post("/ingest_now")
async def ingest_now():
    try:
        ingest_documents()
        return JSONResponse({"status":"ok", "message":"ingestion triggered"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask")
async def ask(req: Request):
    body = await req.json()
    query = body.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="query missing")
    # embed query
    q_vector = embed_text(query)
    # embed_text returns list of vectors if passed list; handle both
    if isinstance(q_vector, list) and isinstance(q_vector[0], list):
        q_vector = q_vector[0]
    results = client.search(collection_name=COLLECTION_NAME, query_vector=q_vector, limit=TOP_K, with_payload=True)
    context = "\n---\n".join([r.payload.get("text", "") for r in results])
    prompt = f"Use the following document snippets to answer the question.\n\n{context}\n\nQuestion: {query}\nAnswer:"
    try:
        resp = requests.post(f"{OLLAMA_URL}/v1/completions", json={"model": OLLAMA_MODEL, "prompt": prompt, "max_tokens":512})
        resp.raise_for_status()
        out = resp.json()
        # handle different Ollama reply shapes
        answer = out.get("completion") or out.get("result") or out
        return JSONResponse({"answer": answer})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama request failed: {e}")

@app.post("/ask_stream")
async def ask_stream(req: Request):
    body = await req.json()
    query = body.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="query missing")
    q_vector = embed_text(query)
    if isinstance(q_vector, list) and isinstance(q_vector[0], list):
        q_vector = q_vector[0]
    results = client.search(collection_name=COLLECTION_NAME, query_vector=q_vector, limit=TOP_K, with_payload=True)
    context = "\n---\n".join([r.payload.get("text", "") for r in results])
    prompt = f"Use the following document snippets to answer the question.\n\n{context}\n\nQuestion: {query}\nAnswer:"

    # Stream from Ollama - uses its streaming completions if available
    def event_generator():
        with requests.post(f"{OLLAMA_URL}/v1/completions", json={"model": OLLAMA_MODEL, "prompt": prompt, "max_tokens":512, "stream": True}, stream=True) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if line:
                    try:
                        data = line.decode("utf-8")
                        # pass raw chunk (Front-end should handle incremental appends)
                        yield data
                    except Exception:
                        continue

    return EventSourceResponse(event_generator())
