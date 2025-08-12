"""
AI Charlotte - Personal RAG Chatbot
Copyright (c) 2025 Charlotte Qazi

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

from fastapi import FastAPI

from backend.api.routes import router
from backend.core.config import settings

app = FastAPI(title="AI Charlotte RAG Backend")

app.include_router(router, prefix="/api")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"} 