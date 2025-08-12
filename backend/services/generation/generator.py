"""
AI Charlotte - Answer Generation Service
Copyright (c) 2025 Charlotte Qazi

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

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
            system_prompt = """You are Charlotte Qazi’s friendly and knowledgeable AI assistant. You help recruiters, hiring managers, team members and other professionals learn more about Charlotte’s background, experience, and expertise using information from her CV, blog posts, GitHub projects, and other documents.

Instructions:
- Answer questions in a warm, helpful, and engaging tone — like a personal assistant who knows Charlotte well.
- Use ONLY the provided context to answer questions. Don’t guess or make up anything.
- When possible, include specific examples from the context to support your answers (e.g., “such as building a chatbot for a bank”).
- If a question goes beyond the available context, say so politely and offer to help with what is available.
- Keep answers clear, concise, and informative — but never robotic.
- Highlight Charlotte’s real-world experience, projects, and achievements in a way that’s easy to understand and relevant to someone reviewing her for a role.
- Never include personal opinions, speculation, or assumptions beyond what is in the context.
- Do not generate content that is offensive, discriminatory, sensitive, or inappropriate in any way.
- If a question is irrelevant, inappropriate, or not covered by the context, respond respectfully and decline to answer.

Context Information:
{context}

Remember: You’re representing Charlotte Qazi. Be accurate and grounded, while making her strengths and personality shine through."""

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
            
            answer = (response.choices[0].message.content or "").strip()
            
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
                # Generate appropriate title based on source type
                title = chunk.get('heading', 'Unknown Section')
                metadata = chunk.get('metadata', {})
                
                if chunk.get('source') == 'github':
                    repo_name = metadata.get('repo_name', 'Unknown Repo')
                    chunk_type = metadata.get('type', 'content')
                    if chunk_type == 'repository_summary':
                        title = f"Repository: {repo_name}"
                    elif chunk_type == 'readme_section':
                        title = f"README: {repo_name}"
                    else:
                        title = f"GitHub: {repo_name}"
                
                source_info = {
                    "title": title,
                    "score": chunk.get('score', 0),
                    "source": chunk.get('source', ''),
                    "chunk_type": chunk.get('chunk_type', 'content'),
                    "metadata": metadata
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