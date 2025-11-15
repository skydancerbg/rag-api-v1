# Version: v1.2.0
# Description: Add manual /ingest endpoint while keeping all existing endpoints

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any

from ingest_module import ingest_docs
# Assuming these were already in your latest main.py
from rag_api.ask_module import ask_query
from rag_api.list_module import list_docs
from rag_api.config_module import CONFIG

app = FastAPI(title="RAG API v1.2.0")

# ---------------- Middleware ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust as needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Models ----------------

class AskRequest(BaseModel):
    query: str

# ---------------- Existing Endpoints ----------------

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/list-docs")
async def list_documents():
    return list_docs()

@app.post("/ask")
async def ask(request: AskRequest):
    answer = ask_query(request.query)
    return {"answer": answer}

# ---------------- New v1.2.0 Endpoint ----------------

@app.post("/ingest")
async def manual_ingest(background_tasks: BackgroundTasks):
    """
    Trigger ingestion manually.
    Runs in background so API remains responsive.
    """
    background_tasks.add_task(ingest_docs)
    return {"status": "ingestion started"}

# ---------------- Startup / Shutdown ----------------

@app.on_event("startup")
async def startup_event():
    # Optional: startup tasks here
    print("RAG API v1.2.0 starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    # Optional: cleanup tasks here
    print("RAG API v1.2.0 shutting down...")
