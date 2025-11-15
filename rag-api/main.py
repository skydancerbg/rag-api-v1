import uvicorn
from fastapi import FastAPI
from rag_api.ingest_module import ingest_docs   # FIXED IMPORT
from rag_api.query_module import query_rag

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest")
async def ingest_endpoint(payload: dict):
    return ingest_docs(payload)

@app.post("/query")
async def query_endpoint(payload: dict):
    question = payload.get("question", "")
    return query_rag(question)

if __name__ == "__main__":
    uvicorn.run("rag_api.main:app", host="0.0.0.0", port=5005)
