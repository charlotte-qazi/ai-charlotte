"""
AI Charlotte - Vector Retrieval Service
Copyright (c) 2025 Charlotte Qazi

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

from typing import List, Dict, Any
import logging
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from backend.core.config import settings

logger = logging.getLogger(__name__)


class Retriever:
    def __init__(self, collection_name: str = "ai_charlotte") -> None:
        self.collection_name = collection_name
        self.openai_client = OpenAI(api_key=settings.openai_api_key)
        self.qdrant_client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )

    async def retrieve(self, query: str, top_k: int = 5, min_score: float = 0.7) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query using semantic search.
        
        Args:
            query: User's question/query
            top_k: Number of top chunks to retrieve
            min_score: Minimum similarity score (0-1)
            
        Returns:
            List of relevant chunks with metadata and scores
        """
        try:
            # Generate embedding for the query
            logger.info(f"🔍 Retrieving for query: '{query[:50]}...'")
            
            embedding_response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            query_embedding = embedding_response.data[0].embedding
            
            # Search Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=min_score,
                with_payload=True,
                with_vectors=False
            )
            
            # Format results
            retrieved_chunks = []
            for result in search_results:
                chunk_data = {
                    "id": result.id,
                    "text": result.payload.get("text", ""),
                    "source": result.payload.get("source", ""),
                    "heading": result.payload.get("heading", ""),
                    "chunk_type": result.payload.get("chunk_type", ""),
                    "word_count": result.payload.get("word_count", 0),
                    "score": float(result.score),
                    "metadata": result.payload.get("metadata", {})
                }
                retrieved_chunks.append(chunk_data)
            
            logger.info(f"📊 Retrieved {len(retrieved_chunks)} chunks (min_score: {min_score})")
            for i, chunk in enumerate(retrieved_chunks):
                logger.info(f"   {i+1}. '{chunk['heading']}' (score: {chunk['score']:.3f})")
            
            return retrieved_chunks
            
        except Exception as e:
            logger.error(f"❌ Retrieval failed: {e}")
            raise

    # TODO: Am I using this?
    async def retrieve_by_source(self, query: str, source: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve chunks filtered by source."""
        try:
            embedding_response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            query_embedding = embedding_response.data[0].embedding
            
            # Search with source filter
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="source",
                            match=MatchValue(value=source)
                        )
                    ]
                ),
                limit=top_k,
                with_payload=True,
                with_vectors=False
            )
            
            return [
                {
                    "id": result.id,
                    "text": result.payload.get("text", ""),
                    "source": result.payload.get("source", ""),
                    "heading": result.payload.get("heading", ""),
                    "score": float(result.score),
                    "metadata": result.payload.get("metadata", {})
                }
                for result in search_results
            ]
            
        except Exception as e:
            logger.error(f"❌ Source-filtered retrieval failed: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check if retrieval system is healthy."""
        try:
            # Check Qdrant connection
            collections = self.qdrant_client.get_collections()
            collection_exists = any(c.name == self.collection_name for c in collections.collections)
            
            if collection_exists:
                collection_info = self.qdrant_client.get_collection(self.collection_name)
                return {
                    "status": "healthy",
                    "collection": self.collection_name,
                    "points_count": collection_info.points_count,
                    "vector_size": collection_info.config.params.vectors.size
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"Collection '{self.collection_name}' not found"
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            } 