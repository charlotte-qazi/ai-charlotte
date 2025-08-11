from typing import List, Dict, Any
import logging
from openai import OpenAI

from backend.core.config import settings

logger = logging.getLogger(__name__)


class AnswerGenerator:
    def __init__(self, model: str = "gpt-3.5-turbo") -> None:
        self.model = model
        self.openai_client = OpenAI(api_key=settings.openai_api_key)

    async def generate(self, question: str, contexts: List[Dict[str, Any]]) -> str:
        """
        Generate an answer using retrieved contexts and OpenAI's LLM.
        
        Args:
            question: User's question
            contexts: List of retrieved chunks with text and metadata
            
        Returns:
            Generated answer string
        """
        try:
            logger.info(f"🤖 Generating answer for: '{question[:50]}...'")
            logger.info(f"📚 Using {len(contexts)} context chunks")
            
            # Build context string from retrieved chunks
            context_parts = []
            for i, chunk in enumerate(contexts, 1):
                heading = chunk.get('heading', 'Unknown')
                text = chunk.get('text', '')
                score = chunk.get('score', 0)
                context_parts.append(f"[Context {i} - {heading} (relevance: {score:.2f})]:\n{text}")
            
            context_string = "\n\n".join(context_parts)
            
            # Create the RAG prompt
            system_prompt = """You are Charlotte Qazi's AI assistant. You help answer questions about Charlotte's background, experience, and expertise based on her CV and other documents.

Instructions:
- Answer questions accurately using ONLY the provided context
- If the context doesn't contain enough information, say so politely
- Be conversational and helpful, as if you're Charlotte's personal assistant
- Include specific details from the context when relevant
- If asked about experience, mention specific companies, roles, and achievements
- Keep answers concise but informative

Context Information:
{context}

Remember: You are representing Charlotte Qazi, so speak knowledgeably about her background while being helpful and professional."""

            user_prompt = f"Question: {question}\n\nPlease provide a helpful answer based on the context above."

            # Generate response
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt.format(context=context_string)},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                top_p=0.9
            )
            
            answer = response.choices[0].message.content.strip()
            
            logger.info(f"✅ Generated answer ({len(answer)} chars)")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Answer generation failed: {e}")
            raise

    async def generate_with_sources(self, question: str, contexts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate answer and return with source information."""
        try:
            answer = await self.generate(question, contexts)
            
            # Format sources from contexts
            sources = []
            for chunk in contexts:
                source_info = {
                    "title": chunk.get('heading', 'Unknown Section'),
                    "score": chunk.get('score', 0),
                    "source": chunk.get('source', ''),
                    "chunk_type": chunk.get('chunk_type', 'content')
                }
                sources.append(source_info)
            
            return {
                "answer": answer,
                "sources": sources,
                "context_count": len(contexts)
            }
            
        except Exception as e:
            logger.error(f"❌ Answer generation with sources failed: {e}")
            raise 