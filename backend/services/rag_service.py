from typing import Dict, Any
import logging

from backend.services.retrieval.retriever import Retriever
from backend.services.generation.generator import AnswerGenerator
from backend.schemas.chat import ChatResponse, Source

logger = logging.getLogger(__name__)


class RAGService:
    """
    Unified RAG (Retrieval-Augmented Generation) service.
    Combines retrieval and generation for question answering.
    """
    
    def __init__(self, collection_name: str = "ai_charlotte") -> None:
        self.retriever = Retriever(collection_name=collection_name)
        self.generator = AnswerGenerator()
    
    async def answer_question(
        self, 
        question: str, 
        top_k: int = 3, 
        min_score: float = 0.6
    ) -> ChatResponse:
        """
        Answer a question using RAG pipeline.
        
        Args:
            question: User's question
            top_k: Number of chunks to retrieve
            min_score: Minimum similarity score for retrieval
            
        Returns:
            ChatResponse with answer and sources
        """
        try:
            logger.info(f"🎯 RAG pipeline starting for: '{question[:50]}...'")
            
            # Step 1: Retrieve relevant contexts
            contexts = await self.retriever.retrieve(
                query=question, 
                top_k=top_k, 
                min_score=min_score
            )
            
            if not contexts:
                logger.warning("⚠️ No relevant contexts found")
                return ChatResponse(
                    answer="I don't have enough information in my knowledge base to answer that question. Could you try rephrasing or asking about Charlotte's professional experience, education, or skills?",
                    sources=[]
                )
            
            # Step 2: Generate answer using contexts
            result = await self.generator.generate_with_sources(question, contexts)
            
            # Step 3: Format sources for response
            sources = []
            for source_info in result["sources"]:
                source = Source(
                    title=source_info["title"],
                    url=None,  # Could add URL if documents have them
                    score=source_info["score"]
                )
                sources.append(source)
            
            response = ChatResponse(
                answer=result["answer"],
                sources=sources
            )
            
            logger.info(f"✅ RAG pipeline completed: {len(result['answer'])} chars, {len(sources)} sources")
            return response
            
        except Exception as e:
            logger.error(f"❌ RAG pipeline failed: {e}")
            return ChatResponse(
                answer="I'm sorry, I encountered an error while processing your question. Please try again.",
                sources=[]
            )
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if RAG service is healthy."""
        try:
            retrieval_health = await self.retriever.health_check()
            
            return {
                "status": "healthy" if retrieval_health["status"] == "healthy" else "unhealthy",
                "retrieval": retrieval_health,
                "generation": {"status": "healthy", "model": self.generator.model}
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            } 