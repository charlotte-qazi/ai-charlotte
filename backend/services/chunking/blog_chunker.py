"""
AI Charlotte - Blog Content Chunker
Copyright (c) 2025 Charlotte Qazi

Specialized chunker for blog posts, optimized for Medium and other blog platforms.

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

from typing import List, Dict, Any
import re
from datetime import datetime


class BlogChunker:
    """Chunks blog posts into semantically meaningful segments for RAG."""
    
    def __init__(self, target_words: int = 200, max_words: int = 400, min_words: int = 50):
        """
        Initialize the blog chunker.
        
        Args:
            target_words: Target words per chunk (default: 200)
            max_words: Maximum words per chunk (default: 400)
            min_words: Minimum words per chunk (default: 50)
        """
        self.target_words = target_words
        self.max_words = max_words
        self.min_words = min_words
    
    def chunk_blog_post(self, post_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk a blog post into semantic segments.
        
        Args:
            post_data: Dictionary containing blog post data with at least 'content' field
            
        Returns:
            List of chunk dictionaries
        """
        content = post_data.get('content', '')
        if not content:
            return []
        
        # Clean and prepare content
        cleaned_content = self._clean_blog_content(content)
        
        # Create metadata for all chunks
        base_metadata = self._extract_base_metadata(post_data)
        
        # Split into sections based on blog structure
        sections = self._split_into_blog_sections(cleaned_content, post_data)
        
        # Chunk each section
        all_chunks = []
        chunk_index = 0
        
        for section in sections:
            section_chunks = self._chunk_section(section, base_metadata, chunk_index)
            all_chunks.extend(section_chunks)
            chunk_index += len(section_chunks)
        
        return all_chunks
    
    def _clean_blog_content(self, content: str) -> str:
        """Clean blog content of common artifacts."""
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Remove common blog artifacts that might have been missed
        artifacts = [
            r'Share this:.*',
            r'Like this:.*',
            r'Related articles?:.*',
            r'Tags?:\s*[^\n]*',
            r'Categories?:\s*[^\n]*',
            r'Filed under:.*',
        ]
        
        for artifact in artifacts:
            content = re.sub(artifact, '', content, flags=re.IGNORECASE)
        
        return content.strip()
    
    def _extract_base_metadata(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract base metadata that applies to all chunks."""
        return {
            'title': post_data.get('title', 'Untitled'),
            'author': post_data.get('author', 'Unknown'),
            'url': post_data.get('url', ''),
            'published_date': post_data.get('published_date'),
            'tags': post_data.get('tags', []),
            'source': post_data.get('source', 'blog'),
            'word_count_total': post_data.get('word_count', 0),
            'reading_time': post_data.get('reading_time', 0)
        }
    
    def _split_into_blog_sections(self, content: str, post_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Split blog content into logical sections."""
        sections = []
        
        # Try to identify sections by headers
        header_pattern = r'\n\s*#{1,6}\s+([^\n]+)\n'
        header_matches = list(re.finditer(header_pattern, content))
        
        if header_matches:
            # Split by headers
            current_pos = 0
            
            for i, match in enumerate(header_matches):
                # Add content before first header as introduction
                if i == 0 and match.start() > 0:
                    intro_text = content[:match.start()].strip()
                    if len(intro_text.split()) >= self.min_words:
                        sections.append({
                            'text': intro_text,
                            'heading': 'Introduction',
                            'section_type': 'introduction',
                            'position': 0
                        })
                
                # Get section content
                start_pos = match.start()
                end_pos = header_matches[i + 1].start() if i + 1 < len(header_matches) else len(content)
                
                section_text = content[start_pos:end_pos].strip()
                heading = match.group(1).strip()
                
                if len(section_text.split()) >= self.min_words:
                    sections.append({
                        'text': section_text,
                        'heading': heading,
                        'section_type': self._classify_blog_section(heading),
                        'position': i + 1
                    })
        else:
            # No clear headers, split by paragraphs or length
            sections = self._split_by_paragraphs(content)
        
        return sections
    
    def _classify_blog_section(self, heading: str) -> str:
        """Classify blog section based on heading."""
        heading_lower = heading.lower()
        
        # Common blog section patterns
        if any(word in heading_lower for word in ['intro', 'introduction', 'overview', 'background']):
            return 'introduction'
        elif any(word in heading_lower for word in ['conclusion', 'summary', 'final', 'wrap', 'takeaway']):
            return 'conclusion'
        elif any(word in heading_lower for word in ['example', 'case', 'demo', 'tutorial', 'how']):
            return 'example'
        elif any(word in heading_lower for word in ['problem', 'challenge', 'issue', 'pain']):
            return 'problem'
        elif any(word in heading_lower for word in ['solution', 'approach', 'method', 'way']):
            return 'solution'
        elif any(word in heading_lower for word in ['result', 'outcome', 'finding', 'data']):
            return 'results'
        elif any(word in heading_lower for word in ['tip', 'advice', 'recommendation', 'best']):
            return 'tips'
        else:
            return 'content'
    
    def _split_by_paragraphs(self, content: str) -> List[Dict[str, Any]]:
        """Split content by paragraphs when no clear structure is found."""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        sections = []
        
        current_section = []
        current_words = 0
        section_index = 0
        
        for paragraph in paragraphs:
            para_words = len(paragraph.split())
            
            # If adding this paragraph would exceed max_words, start new section
            if current_words + para_words > self.max_words and current_section:
                section_text = '\n\n'.join(current_section)
                sections.append({
                    'text': section_text,
                    'heading': f'Section {section_index + 1}',
                    'section_type': 'content',
                    'position': section_index
                })
                
                current_section = [paragraph]
                current_words = para_words
                section_index += 1
            else:
                current_section.append(paragraph)
                current_words += para_words
        
        # Add final section
        if current_section:
            section_text = '\n\n'.join(current_section)
            sections.append({
                'text': section_text,
                'heading': f'Section {section_index + 1}',
                'section_type': 'content',
                'position': section_index
            })
        
        return sections
    
    def _chunk_section(self, section: Dict[str, Any], base_metadata: Dict[str, Any], 
                      start_index: int) -> List[Dict[str, Any]]:
        """Chunk a single section into appropriately sized pieces."""
        text = section['text']
        words = text.split()
        
        if len(words) <= self.max_words:
            # Section fits in one chunk
            return [self._create_chunk(
                text=text,
                index=start_index,
                heading=section['heading'],
                chunk_type=section['section_type'],
                metadata=base_metadata
            )]
        
        # Split large section into multiple chunks
        chunks = []
        current_chunk = []
        current_words = 0
        chunk_index = start_index
        
        # Split by sentences to maintain readability
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            # If adding this sentence would exceed max_words, finalize current chunk
            if current_words + sentence_words > self.max_words and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append(self._create_chunk(
                    text=chunk_text,
                    index=chunk_index,
                    heading=section['heading'],
                    chunk_type=section['section_type'],
                    metadata=base_metadata
                ))
                
                current_chunk = [sentence]
                current_words = sentence_words
                chunk_index += 1
            else:
                current_chunk.append(sentence)
                current_words += sentence_words
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(self._create_chunk(
                text=chunk_text,
                index=chunk_index,
                heading=section['heading'],
                chunk_type=section['section_type'],
                metadata=base_metadata
            ))
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences while preserving meaning."""
        # Simple sentence splitting (can be improved with NLP libraries)
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _create_chunk(self, text: str, index: int, heading: str, chunk_type: str, 
                     metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create a standardized chunk dictionary."""
        word_count = len(text.split())
        
        # Create unique ID
        title_slug = re.sub(r'[^a-zA-Z0-9]+', '-', metadata['title'].lower()).strip('-')
        chunk_id = f"{title_slug}-{index}"
        
        return {
            'id': chunk_id,
            'chunk_index': index,
            'text': text,
            'source': metadata['title'],
            'heading': heading,
            'chunk_type': chunk_type,
            'word_count': word_count,
            'metadata': {
                'title': metadata['title'],
                'author': metadata['author'],
                'url': metadata['url'],
                'published_date': metadata['published_date'].isoformat() if metadata['published_date'] else None,
                'tags': metadata['tags'],
                'source_type': metadata['source'],
                'total_word_count': metadata['word_count_total'],
                'reading_time': metadata['reading_time'],
                'processing_method': 'blog_chunker'
            }
        }
    
    def get_chunking_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics about the chunking results."""
        if not chunks:
            return {'total_chunks': 0}
        
        total_words = sum(chunk['word_count'] for chunk in chunks)
        chunk_types = {}
        
        for chunk in chunks:
            chunk_type = chunk['chunk_type']
            if chunk_type not in chunk_types:
                chunk_types[chunk_type] = 0
            chunk_types[chunk_type] += 1
        
        return {
            'total_chunks': len(chunks),
            'total_words': total_words,
            'avg_words_per_chunk': total_words // len(chunks),
            'min_words': min(chunk['word_count'] for chunk in chunks),
            'max_words': max(chunk['word_count'] for chunk in chunks),
            'chunk_types': chunk_types,
            'headings': [chunk['heading'] for chunk in chunks]
        }


if __name__ == "__main__":
    # Example usage
    sample_post = {
        'title': 'How to Build a RAG System',
        'author': 'Charlotte Qazi',
        'content': '''
        # Introduction
        
        Building a Retrieval-Augmented Generation (RAG) system can seem daunting at first. However, with the right approach and tools, it becomes much more manageable.
        
        # The Problem
        
        Traditional chatbots often struggle with providing accurate, up-to-date information. They're limited to their training data and can't access new information.
        
        # The Solution
        
        RAG systems solve this by combining retrieval of relevant documents with generation capabilities. This allows for more accurate and contextual responses.
        
        # Implementation Steps
        
        Here are the key steps to build a RAG system:
        
        1. Document ingestion and preprocessing
        2. Text chunking and embedding generation
        3. Vector database setup
        4. Retrieval mechanism
        5. Generation with context
        
        # Conclusion
        
        RAG systems represent a powerful approach to building intelligent applications that can provide accurate, contextual responses.
        ''',
        'tags': ['rag', 'ai', 'nlp', 'tutorial'],
        'word_count': 150,
        'reading_time': 2,
        'published_date': datetime.now()
    }
    
    chunker = BlogChunker()
    chunks = chunker.chunk_blog_post(sample_post)
    stats = chunker.get_chunking_stats(chunks)
    
    print(f"Created {stats['total_chunks']} chunks")
    print(f"Average words per chunk: {stats['avg_words_per_chunk']}")
    print(f"Chunk types: {stats['chunk_types']}")
    
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}: {chunk['heading']} ({chunk['word_count']} words)")
        print(f"Type: {chunk['chunk_type']}")
        print(f"Preview: {chunk['text'][:100]}...") 