from fastapi import FastAPI

from backend.api.routes import router
from backend.core.config import settings

app = FastAPI(title="AI Charlotte RAG Backend")

app.include_router(router, prefix="/api")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"} 