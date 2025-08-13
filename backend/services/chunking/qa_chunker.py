"""
AI Charlotte - Q&A Chunking Service
Copyright (c) 2025 Charlotte Qazi

Q&A chunker that creates one chunk per question-answer pair.
Specifically designed for FAQ/Q&A content with ## headers.

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

import re
from typing import List, Dict, Any


class QAChunker:
    """
    Chunker specifically designed for Q&A content.
    Each question (## header) becomes its own chunk with the answer content.
    """
    
    def __init__(self):
        pass
    
    def chunk_qa(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunk Q&A content by splitting at ## headers.
        Each question-answer pair becomes one chunk.
        """
        chunks = []
        
        # Split by ## headers (questions)
        sections = re.split(r'\n\s*##\s*([^\n]+)', text)
        
        # First section before any ## header (if exists)
        intro_text = sections[0].strip()
        
        # Process question-answer pairs
        for i in range(1, len(sections), 2):
            if i + 1 < len(sections):
                question = sections[i].strip()
                answer = sections[i + 1].strip()
                
                # Clean up the question (remove any formatting artifacts)
                question = self._clean_question(question)
                
                # Create the chunk content
                chunk_text = f"Q: {question}\n\nA: {answer}"
                
                chunks.append({
                    'text': chunk_text,
                    'heading': question,
                    'chunk_type': 'qa',
                    'word_count': len(chunk_text.split()),
                    'question': question,
                    'answer': answer
                })
        
        return chunks
    
    def _clean_question(self, question: str) -> str:
        """Clean up question text."""
        # Remove extra whitespace and normalize
        question = re.sub(r'\s+', ' ', question.strip())
        
        # Ensure it ends with a question mark if it looks like a question
        if question and not question.endswith('?') and any(word in question.lower() for word in ['what', 'how', 'why', 'where', 'when', 'who', 'which']):
            question += '?'
        
        return question 