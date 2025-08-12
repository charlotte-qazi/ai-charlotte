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

from backend.schemas.chat import ChatRequest, ChatResponse, CreateUserRequest, CreateUserResponse
from backend.services.rag_service import RAGService
from backend.services.supabase_client import SupabaseClient
from backend.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize services
rag_service = RAGService(collection_name="ai_charlotte")
supabase_client = SupabaseClient()


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


@router.post("/users", response_model=CreateUserResponse)
@limiter.limit(f"{settings.rate_limit_requests}/minute")
async def create_user(request: Request, user_request: CreateUserRequest) -> CreateUserResponse:
    """
    Create a new user after onboarding.
    Saves name, role, and interests in one API call.
    """
    try:
        logger.info(f"👤 Creating user: {user_request.name}")
        
        # Save user to database
        user_id = await supabase_client.create_user(
            name=user_request.name,
            interests=user_request.interests
        )
        
        return CreateUserResponse(user_id=user_id)
        
    except Exception as e:
        logger.error(f"❌ Error creating user: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unable to create user. Please try again."
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