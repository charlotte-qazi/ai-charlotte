"""
AI Charlotte - GitHub Repository Chunker
Copyright (c) 2025 Charlotte Qazi

GitHub repository chunker for processing repository data and README files.
Handles both structured repository metadata and README content.

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class GitHubChunker:
    """
    Chunker for GitHub repository data.
    Handles repository summaries and README content appropriately.
    """
    
    def __init__(self, target_words: int = 150, max_words: int = 200):
        self.target_words = target_words
        self.max_words = max_words
        self.min_words = 10
    
    def chunk_github_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Chunk GitHub documents (repositories and READMEs).
        
        Args:
            documents: List of GitHub documents from ingestion
            
        Returns:
            List of chunked documents with metadata
        """
        chunks = []
        
        for doc in documents:
            try:
                doc_chunks = self._chunk_single_document(doc)
                chunks.extend(doc_chunks)
            except Exception as e:
                logger.error(f"Failed to chunk document {doc.get('repo_name', 'unknown')}: {e}")
                continue
        
        logger.info(f"Generated {len(chunks)} chunks from {len(documents)} GitHub documents")
        return chunks
    
    def _chunk_single_document(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk a single GitHub document based on its type."""
        doc_type = document.get("type", "unknown")
        
        if doc_type == "repository":
            return self._chunk_repository_summary(document)
        elif doc_type == "readme":
            return self._chunk_readme(document)
        else:
            logger.warning(f"Unknown document type: {doc_type}")
            return []
    
    def _chunk_repository_summary(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk repository summary - usually these are concise enough to be single chunks.
        """
        text = document["text"]
        word_count = len(text.split())
        
        # If the repo summary is short enough, keep as single chunk
        if word_count <= self.max_words:
            chunk = {
                "id": f"github_repo_{document['repo_name']}_summary",
                "text": text,
                "source": "github",
                "chunk_index": 0,
                "metadata": {
                    "type": "repository_summary",
                    "repo_name": document["repo_name"],
                    "repo_url": document["repo_url"],
                    "word_count": word_count,
                    **document.get("metadata", {})
                }
            }
            return [chunk]
        
        # If it's too long (unlikely), split it
        return self._split_long_text(
            text=text,
            base_id=f"github_repo_{document['repo_name']}_summary",
            document=document,
            doc_type="repository_summary"
        )
    
    def _chunk_readme(self, document: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk README content - these can be quite long and need proper sectioning.
        """
        text = document["text"]
        repo_name = document["repo_name"]
        
        # Clean the README text
        cleaned_text = self._clean_readme_text(text)
        
        # Try to split by sections first
        sections = self._split_readme_by_sections(cleaned_text)
        
        chunks = []
        for section_idx, section in enumerate(sections):
            section_chunks = self._chunk_readme_section(
                section=section,
                repo_name=repo_name,
                section_idx=section_idx,
                document=document
            )
            chunks.extend(section_chunks)
        
        return chunks
    
    def _clean_readme_text(self, text: str) -> str:
        """Clean README text from markdown artifacts."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Clean up common markdown artifacts
        text = re.sub(r'!\[.*?\]\(.*?\)', '[Image]', text)  # Images
        text = re.sub(r'\[!\[.*?\]\(.*?\)\]\(.*?\)', '[Badge]', text)  # Badges
        
        # Clean up table formatting
        text = re.sub(r'\|[^|\n]*\|', ' ', text)
        text = re.sub(r'\|\s*:?-+:?\s*\|', ' ', text)
        
        # Clean up code blocks but preserve inline code
        text = re.sub(r'```[\s\S]*?```', '[Code Block]', text)
        
        # Normalize line breaks
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        return text.strip()
    
    def _split_readme_by_sections(self, text: str) -> List[str]:
        """Split README by sections (headers)."""
        # Split by markdown headers (# or ##)
        sections = re.split(r'\n(?=#{1,6}\s)', text)
        
        # Filter out empty sections
        sections = [section.strip() for section in sections if section.strip()]
        
        # If no clear sections found, split by double newlines
        if len(sections) <= 1:
            sections = [s.strip() for s in text.split('\n\n') if s.strip()]
        
        # If still only one section and it's long, split by paragraphs
        if len(sections) == 1 and len(sections[0].split()) > self.max_words * 2:
            paragraphs = [p.strip() for p in sections[0].split('\n\n') if p.strip()]
            if len(paragraphs) > 1:
                sections = paragraphs
        
        return sections
    
    def _chunk_readme_section(
        self, 
        section: str, 
        repo_name: str, 
        section_idx: int, 
        document: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Chunk a single README section."""
        word_count = len(section.split())
        
        # If section is small enough, keep as single chunk
        if word_count <= self.max_words:
            chunk = {
                "id": f"github_readme_{repo_name}_section_{section_idx}",
                "text": section,
                "source": "github",
                "chunk_index": section_idx,
                "metadata": {
                    "type": "readme_section",
                    "repo_name": repo_name,
                    "repo_url": document["repo_url"],
                    "section_index": section_idx,
                    "word_count": word_count,
                    **document.get("metadata", {})
                }
            }
            return [chunk]
        
        # If section is too long, split it further
        return self._split_long_text(
            text=section,
            base_id=f"github_readme_{repo_name}_section_{section_idx}",
            document=document,
            doc_type="readme_section",
            section_idx=section_idx
        )
    
    def _split_long_text(
        self, 
        text: str, 
        base_id: str, 
        document: Dict[str, Any],
        doc_type: str,
        section_idx: int = 0
    ) -> List[Dict[str, Any]]:
        """Split long text into appropriately sized chunks."""
        sentences = self._split_into_sentences(text)
        chunks = []
        current_chunk: List[str] = []
        current_word_count = 0
        chunk_idx = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            # If adding this sentence would exceed max_words, create a chunk
            if current_word_count + sentence_words > self.max_words and current_chunk:
                chunk_text = ' '.join(current_chunk)
                if len(chunk_text.split()) >= self.min_words:  # Only create if meets minimum
                    chunk = {
                        "id": f"{base_id}_chunk_{chunk_idx}",
                        "text": chunk_text,
                        "source": "github",
                        "chunk_index": chunk_idx,
                        "metadata": {
                            "type": doc_type,
                            "repo_name": document["repo_name"],
                            "repo_url": document["repo_url"],
                            "section_index": section_idx,
                            "word_count": current_word_count,
                            **document.get("metadata", {})
                        }
                    }
                    chunks.append(chunk)
                    chunk_idx += 1
                
                # Start new chunk
                current_chunk = [sentence]
                current_word_count = sentence_words
            else:
                current_chunk.append(sentence)
                current_word_count += sentence_words
        
        # Add final chunk if it has content
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            if len(chunk_text.split()) >= self.min_words:
                chunk = {
                    "id": f"{base_id}_chunk_{chunk_idx}",
                    "text": chunk_text,
                    "source": "github",
                    "chunk_index": chunk_idx,
                    "metadata": {
                        "type": doc_type,
                        "repo_name": document["repo_name"],
                        "repo_url": document["repo_url"],
                        "section_index": section_idx,
                        "word_count": current_word_count,
                        **document.get("metadata", {})
                    }
                }
                chunks.append(chunk)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting - can be improved
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Clean up sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Handle very short sentences by combining them
        combined_sentences = []
        current_sentence = ""
        
        for sentence in sentences:
            if len(sentence.split()) < 5 and current_sentence:  # Very short sentence
                current_sentence += " " + sentence
            else:
                if current_sentence:
                    combined_sentences.append(current_sentence)
                current_sentence = sentence
        
        if current_sentence:
            combined_sentences.append(current_sentence)
        
        return combined_sentences
    
    def get_chunk_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about the chunked documents."""
        if not chunks:
            return {"total_chunks": 0}
        
        word_counts = [chunk["metadata"]["word_count"] for chunk in chunks]
        repo_types: Dict[str, int] = {}
        
        for chunk in chunks:
            chunk_type = chunk["metadata"]["type"]
            repo_types[chunk_type] = repo_types.get(chunk_type, 0) + 1
        
        return {
            "total_chunks": len(chunks),
            "avg_words_per_chunk": sum(word_counts) / len(word_counts),
            "min_words": min(word_counts),
            "max_words": max(word_counts),
            "chunk_types": repo_types,
            "repositories": len(set(chunk["metadata"]["repo_name"] for chunk in chunks))
        } 