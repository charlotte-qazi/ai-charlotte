import re
from typing import Any, Dict, List


class SmartChunker:
    def __init__(self, target_words: int = 200, max_words: int = 350) -> None:
        self.target_words = target_words
        self.max_words = max_words

    def chunk_cv_markdown(self, text: str) -> List[Dict[str, Any]]:
        """Smart chunking for CV format with bold headings and job sections."""
        chunks = []
        
        # Split by major sections first
        # Look for patterns like "**Professional Experience**" or "---"
        sections = re.split(r'\n\s*---\s*\n|\n\s*\*\*([^*]+)\*\*\s*\n', text)
        
        current_heading = "Profile"
        
        for i, section in enumerate(sections):
            section = section.strip()
            if not section:
                continue
            
            # If this section is very short, it might be a heading
            words = section.split()
            if len(words) <= 5 and any(keyword in section.lower() for keyword in 
                                     ['experience', 'education', 'skills', 'projects', 'contact']):
                current_heading = section
                continue
            
            # Skip very short sections
            if len(words) < 20:
                continue
            
            # Now chunk this section intelligently
            section_chunks = self._chunk_section_by_jobs(section, current_heading)
            chunks.extend(section_chunks)
        
        return chunks

    def chunk_markdown(self, text: str) -> List[Dict[str, Any]]:
        """Smart chunking for general Markdown with headers."""
        chunks = []
        lines = text.split('\n')
        
        current_section = {'heading': 'Introduction', 'content': [], 'level': 0, 'start': 0}
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Skip empty lines and comments
            if not line_stripped or line_stripped.startswith('<!--') or line_stripped.endswith('-->'):
                continue
            
            # Check for markdown headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line_stripped)
            
            if header_match:
                # Save previous section if it has substantial content
                if current_section['content']:
                    section_text = '\n'.join(current_section['content']).strip()
                    words = section_text.split()
                    if len(words) > 10:  # At least 10 words
                        if len(words) <= self.max_words:
                            chunks.append({
                                'text': section_text,
                                'heading': current_section['heading'],
                                'level': current_section['level'],
                                'type': 'markdown_section',
                                'word_count': len(words),
                                'start_line': current_section['start'],
                                'end_line': i - 1
                            })
                        else:
                            # Split large sections
                            sub_chunks = self._split_large_section(
                                section_text, current_section['heading']
                            )
                            chunks.extend(sub_chunks)
                
                # Start new section
                level = len(header_match.group(1))
                heading = header_match.group(2).strip()
                current_section = {
                    'heading': heading,
                    'content': [line],
                    'level': level,
                    'start': i
                }
            else:
                current_section['content'].append(line)
        
        # Don't forget the last section
        if current_section['content']:
            section_text = '\n'.join(current_section['content']).strip()
            words = section_text.split()
            if len(words) > 10:
                if len(words) <= self.max_words:
                    chunks.append({
                        'text': section_text,
                        'heading': current_section['heading'],
                        'level': current_section['level'],
                        'type': 'markdown_section',
                        'word_count': len(words),
                        'start_line': current_section['start'],
                        'end_line': len(lines) - 1
                    })
                else:
                    sub_chunks = self._split_large_section(
                        section_text, current_section['heading']
                    )
                    chunks.extend(sub_chunks)
        
        return chunks

    def _chunk_section_by_jobs(self, text: str, section_heading: str) -> List[Dict[str, Any]]:
        """Chunk a section by detecting job roles and logical breaks."""
        chunks = []
        
        # Split by job patterns - look for bold job titles or company names
        job_patterns = [
            r'\n\s*\*\*([^*]+)\*\*\s*\n',  # **Job Title**
            r'\n([A-Z][^.!?]*(?:Engineer|Developer|Manager|Analyst|Consultant|Lead|Director)[^.!?]*)\n',
            r'\n([A-Z][^.!?]*(?:BCG|Google|Microsoft|Amazon|Apple)[^.!?]*)\n',
        ]
        
        # Try to split by job sections
        parts = []
        remaining_text = text
        
        for pattern in job_patterns:
            matches = list(re.finditer(pattern, remaining_text, re.IGNORECASE))
            if matches:
                last_end = 0
                for match in matches:
                    # Add text before this match
                    if match.start() > last_end:
                        before_text = remaining_text[last_end:match.start()].strip()
                        if before_text and len(before_text.split()) > 10:
                            parts.append({
                                'text': before_text,
                                'type': 'content',
                                'heading': section_heading
                            })
                    
                    # Add the job section (from match to next match or end)
                    next_match_start = matches[matches.index(match) + 1].start() if matches.index(match) + 1 < len(matches) else len(remaining_text)
                    job_text = remaining_text[match.start():next_match_start].strip()
                    
                    if job_text and len(job_text.split()) > 15:
                        job_title = match.group(1) if match.groups() else "Job Section"
                        parts.append({
                            'text': job_text,
                            'type': 'job',
                            'heading': f"{section_heading}: {job_title}",
                            'job_title': job_title
                        })
                    
                    last_end = next_match_start
                
                # Add any remaining text
                if last_end < len(remaining_text):
                    remaining_text_part = remaining_text[last_end:].strip()
                    if remaining_text_part and len(remaining_text_part.split()) > 10:
                        parts.append({
                            'text': remaining_text_part,
                            'type': 'content',
                            'heading': section_heading
                        })
                break
        
        # If no job patterns found, split by paragraphs
        if not parts:
            paragraphs = re.split(r'\n\s*\n', text)
            current_chunk = ""
            chunk_count = 0
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                
                # Would adding this paragraph exceed max words?
                combined = (current_chunk + "\n\n" + paragraph).strip()
                if len(combined.split()) > self.max_words and len(current_chunk.split()) >= 50:
                    parts.append({
                        'text': current_chunk.strip(),
                        'type': 'content',
                        'heading': f"{section_heading}" + (f" (Part {chunk_count + 1})" if chunk_count > 0 else "")
                    })
                    chunk_count += 1
                    current_chunk = paragraph
                else:
                    current_chunk = combined
            
            # Add the last chunk
            if current_chunk and len(current_chunk.split()) >= 20:
                parts.append({
                    'text': current_chunk.strip(),
                    'type': 'content',
                    'heading': f"{section_heading}" + (f" (Part {chunk_count + 1})" if chunk_count > 0 else "")
                })
        
        # Convert parts to chunks
        for part in parts:
            word_count = len(part['text'].split())
            if word_count >= 20:  # Only include substantial chunks
                chunks.append({
                    'text': part['text'],
                    'heading': part['heading'],
                    'type': part['type'],
                    'word_count': word_count,
                    'parent_heading': section_heading
                })
        
        return chunks

    def _split_large_section(self, text: str, heading: str) -> List[Dict[str, Any]]:
        """Split a large section into smaller pieces while preserving context."""
        chunks = []
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk = ""
        chunk_counter = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph would exceed max size, save current chunk
            combined = (current_chunk + "\n\n" + paragraph).strip()
            if len(combined.split()) > self.max_words and len(current_chunk.split()) >= 50:
                chunks.append({
                    'text': current_chunk.strip(),
                    'heading': f"{heading}" + (f" (Part {chunk_counter + 1})" if chunk_counter > 0 else ""),
                    'type': 'smart_section',
                    'word_count': len(current_chunk.split()),
                    'parent_heading': heading
                })
                chunk_counter += 1
                current_chunk = paragraph
            else:
                current_chunk = combined
        
        # Add the last chunk
        if current_chunk and len(current_chunk.split()) >= 20:
            chunks.append({
                'text': current_chunk.strip(),
                'heading': f"{heading}" + (f" (Part {chunk_counter + 1})" if chunk_counter > 0 else ""),
                'type': 'smart_section',
                'word_count': len(current_chunk.split()),
                'parent_heading': heading
            })
        
        return chunks if chunks else [{
            'text': text,
            'heading': heading,
            'type': 'smart_section',
            'word_count': len(text.split()),
            'parent_heading': heading
        }] 