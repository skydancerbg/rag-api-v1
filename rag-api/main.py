# /opt/rag-api/rag_api/main.py v1.1.4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rag_api.ingest_module import ingest_docs, list_docs, ask_query
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
import asyncio

# Config from environment
INGEST_INTERVAL_MIN = int(os.getenv("INGEST_INTERVAL_MIN", "10"))

app = FastAPI(title="RAG API v1.1.4")

# CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = AsyncIOScheduler()

@app.on_event("startup")
async def startup_event():
    """Start APScheduler after FastAPI event loop is running"""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        scheduler.add_job(ingest_docs, "interval", minutes=INGEST_INTERVAL_MIN)
        scheduler.start()
    else:
        # fallback in case event loop not running
        loop.run_until_complete(asyncio.sleep(0))
        scheduler.add_job(ingest_docs, "interval", minutes=INGEST_INTERVAL_MIN)
        scheduler.start()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/list-docs")
async def list_documents():
    return list_docs()


@app.post("/ingest")
async def ingest():
    ingest_docs()
    return {"status": "ingestion triggered"}


@app.post("/ask")
async def ask(payload: dict):
    query = payload.get("query", "")
    if not query:
        return {"error": "Missing 'query' in request body"}
    result = ask_query(query)
    return {"result": result}
