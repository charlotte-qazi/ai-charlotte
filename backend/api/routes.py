"""
AI Charlotte - Personal RAG Chatbot API Routes
Copyright (c) 2025 Charlotte Qazi

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

import logging
from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.rag_service import RAGService
from backend.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize RAG service
rag_service = RAGService(collection_name="ai_charlotte")


@router.post("/chat", response_model=ChatResponse)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def chat(request: Request, chat_request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint powered by RAG (Retrieval-Augmented Generation).
    Answers questions about Charlotte Qazi using her CV and documents.
    """
    try:
        logger.info(f"💬 Chat request: '{chat_request.message[:100]}...'")
        
        # Use RAG service to answer the question
        response = await rag_service.answer_question(
            question=chat_request.message,
            top_k=3,  # Retrieve top 3 most relevant chunks
            min_score=0.3  # Minimum similarity score (lowered further for better recall)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Chat endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail="I'm experiencing technical difficulties. Please try again."
        )


@router.get("/health")
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def health_check(request: Request):
    """Health check endpoint for the RAG system."""
    try:
        health_status = await rag_service.health_check()
        return health_status
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)} 