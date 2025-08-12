"""
AI Charlotte - Text Embedding Service
Copyright (c) 2025 Charlotte Qazi

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

from typing import List, Optional
import openai
from openai import OpenAI

# Uses OpenAI's text-embedding-3-small model by default to convert text into vectors
class EmbeddingClient:
    def __init__(self, api_key: Optional[str], model: str = "text-embedding-3-small") -> None:
        if not api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed_text(self, text: str) -> List[float]:
        """Embed a single text string."""
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding

    # Batch send texts to OpenAI API to avoid rate limits and improve efficiency
    def embed_texts(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Embed multiple texts with batching for efficiency."""
        if not texts:
            return []
        
        embeddings: List[List[float]] = []
        
        # Process in batches to avoid API limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            response = self.client.embeddings.create(
                model=self.model,
                input=batch,
                encoding_format="float"
            )
            
            batch_embeddings = [data.embedding for data in response.data]
            embeddings.extend(batch_embeddings)
        
        return embeddings

    # Get the dimension of embeddings for this model for Qdrant vector store to help work out similarity of vectors
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings for this model."""
        # text-embedding-3-small has 1536 dimensions
        # text-embedding-3-large has 3072 dimensions
        if "small" in self.model:
            return 1536
        elif "large" in self.model:
            return 3072
        else:
            # Default to small for unknown models
            return 1536 