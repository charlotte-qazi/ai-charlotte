import logging
from fastapi import APIRouter, HTTPException

from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.rag_service import RAGService

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize RAG service
rag_service = RAGService(collection_name="ai_charlotte")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Chat endpoint powered by RAG (Retrieval-Augmented Generation).
    Answers questions about Charlotte Qazi using her CV and documents.
    """
    try:
        logger.info(f"💬 Chat request: '{request.message[:100]}...'")
        
        # Use RAG service to answer the question
        response = await rag_service.answer_question(
            question=request.message,
            top_k=3,  # Retrieve top 3 most relevant chunks
            min_score=0.4  # Minimum similarity score (lowered for better recall)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Chat endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail="I'm experiencing technical difficulties. Please try again."
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for the RAG system."""
    try:
        health_status = await rag_service.health_check()
        return health_status
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)} 