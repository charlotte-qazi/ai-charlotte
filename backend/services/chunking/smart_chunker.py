import re
from typing import Any, Dict, List


class SmartChunker:
    def __init__(self, target_words: int = 100, max_words: int = 150) -> None:
        """Reduced chunk sizes for better granularity"""
        self.target_words = target_words
        self.max_words = max_words

    def chunk_cv_markdown(self, text: str) -> List[Dict[str, Any]]:
        """Enhanced CV chunking with better job and education detection."""
        chunks = []
        
        # Clean up the text first
        text = self._clean_markdown_text(text)
        
        # Split by major sections using multiple patterns
        section_patterns = [
            r'\n\s*---\s*\n',  # Horizontal rules
            r'\n\s*\*\*([^*]+)\*\*\s*\n',  # Bold headings like **Professional Experience**
            r'\n\s*#+\s*([^\n]+)\n',  # Markdown headers like ## Education
        ]
        
        sections = self._split_by_patterns(text, section_patterns)
        
        for section_info in sections:
            section_text = section_info['text'].strip()
            section_heading = section_info.get('heading', 'Unknown')
            
            if len(section_text.split()) < 10:  # Skip very short sections
                continue
            
            # Handle different section types
            if any(keyword in section_heading.lower() for keyword in ['experience', 'work', 'career']):
                section_chunks = self._chunk_experience_section(section_text, section_heading)
            elif any(keyword in section_heading.lower() for keyword in ['education', 'qualifications', 'degree']):
                section_chunks = self._chunk_education_section(section_text, section_heading)
            elif any(keyword in section_heading.lower() for keyword in ['skills', 'expertise', 'technologies']):
                section_chunks = self._chunk_skills_section(section_text, section_heading)
            else:
                section_chunks = self._chunk_general_section(section_text, section_heading)
            
            chunks.extend(section_chunks)
        
        return chunks

    def _clean_markdown_text(self, text: str) -> str:
        """Clean up markdown formatting issues."""
        # Fix table formatting issues
        text = re.sub(r'\|\s*\|\s*', ' ', text)
        text = re.sub(r'\|\s*:\-+\s*\|\s*', ' ', text)
        text = re.sub(r'\|\s*', ' ', text)
        
        # Clean up multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()

    def _split_by_patterns(self, text: str, patterns: List[str]) -> List[Dict[str, Any]]:
        """Split text by multiple patterns and extract headings."""
        sections = []
        current_pos = 0
        current_heading = "Introduction"
        
        # Find all matches for all patterns
        all_matches = []
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                heading = match.group(1) if match.groups() else "Section"
                all_matches.append({
                    'start': match.start(),
                    'end': match.end(),
                    'heading': heading.strip(),
                    'full_match': match.group(0)
                })
        
        # Sort matches by position
        all_matches.sort(key=lambda x: x['start'])
        
        # Extract sections
        for i, match in enumerate(all_matches):
            # Add text before this match as a section
            if match['start'] > current_pos:
                section_text = text[current_pos:match['start']].strip()
                if section_text and len(section_text.split()) > 5:
                    sections.append({
                        'text': section_text,
                        'heading': current_heading
                    })
            
            # Update current heading and position
            current_heading = match['heading']
            current_pos = match['end']
        
        # Add final section
        if current_pos < len(text):
            section_text = text[current_pos:].strip()
            if section_text and len(section_text.split()) > 5:
                sections.append({
                    'text': section_text,
                    'heading': current_heading
                })
        
        return sections

    def _chunk_experience_section(self, text: str, heading: str) -> List[Dict[str, Any]]:
        """Chunk experience section by individual jobs."""
        chunks = []
        
        # Look for job patterns: company names, dates, job titles
        job_patterns = [
            r'([A-Z][^,\n]*(?:Ltd|Inc|Corp|Company|Group|X|Ventures|Events)[^,\n]*),?\s*([^|]*)\s*\|\s*([^|]*)',
            r'([A-Z][^,\n]*),\s*([^|]*)\s*\|\s*([^|]*)',
            r'\*\*([^*]+)\*\*[^|]*\|[^|]*\|[^|]*',
        ]
        
        # Split by job entries
        job_sections = []
        remaining_text = text
        
        # Try to identify individual job entries
        paragraphs = text.split('\n\n')
        current_job = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check if this looks like a new job (has company name pattern)
            is_new_job = any(re.search(pattern, paragraph) for pattern in job_patterns)
            
            if is_new_job and current_job and len(current_job.split()) > 15:
                job_sections.append(current_job.strip())
                current_job = paragraph
            else:
                current_job += "\n\n" + paragraph if current_job else paragraph
        
        # Add the last job
        if current_job and len(current_job.split()) > 15:
            job_sections.append(current_job.strip())
        
        # If no clear job sections found, split by size
        if not job_sections:
            size_chunks = self._split_by_size(text, self.max_words, heading)
            job_sections = [chunk['text'] for chunk in size_chunks]
        
        # Create chunks for each job
        for i, job_text in enumerate(job_sections):
            words = job_text.split()
            if len(words) < 10:  # Skip very short sections
                continue
            
            # Extract company name for better heading
            company_match = re.search(r'^([^,|\n]+)', job_text.strip())
            job_heading = company_match.group(1).strip() if company_match else f"{heading} (Job {i+1})"
            
            chunks.append({
                'text': job_text,
                'heading': job_heading,
                'type': 'job_experience',
                'word_count': len(words),
                'parent_heading': heading
            })
        
        return chunks

    def _chunk_education_section(self, text: str, heading: str) -> List[Dict[str, Any]]:
        """Chunk education section by degrees/institutions."""
        chunks = []
        
        # Look for education patterns: universities, degrees, dates
        edu_patterns = [
            r'([^,\n]*(?:University|College|School|Institute)[^,\n]*)',
            r'([^,\n]*(?:BSc|MSc|BA|MA|PhD|Degree)[^,\n]*)',
            r'([^|]*)\s*\|\s*([^|]*)',  # Institution | Degree pattern
        ]
        
        # Split by educational entries
        paragraphs = text.split('\n\n')
        current_edu = ""
        edu_sections = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check if this looks like a new education entry
            is_new_edu = any(re.search(pattern, paragraph, re.IGNORECASE) for pattern in edu_patterns)
            
            if is_new_edu and current_edu and len(current_edu.split()) > 10:
                edu_sections.append(current_edu.strip())
                current_edu = paragraph
            else:
                current_edu += "\n\n" + paragraph if current_edu else paragraph
        
        # Add the last education entry
        if current_edu and len(current_edu.split()) > 10:
            edu_sections.append(current_edu.strip())
        
        # If no clear education sections, treat as single chunk
        if not edu_sections and len(text.split()) > 10:
            edu_sections = [text]
        
        # Create chunks for each education entry
        for i, edu_text in enumerate(edu_sections):
            words = edu_text.split()
            if len(words) < 5:
                continue
            
            # Extract institution name for better heading
            institution_match = re.search(r'([^,|\n]*(?:University|College|School|Institute)[^,|\n]*)', edu_text, re.IGNORECASE)
            edu_heading = institution_match.group(1).strip() if institution_match else f"{heading} ({i+1})"
            
            chunks.append({
                'text': edu_text,
                'heading': edu_heading,
                'type': 'education',
                'word_count': len(words),
                'parent_heading': heading
            })
        
        return chunks

    def _chunk_skills_section(self, text: str, heading: str) -> List[Dict[str, Any]]:
        """Chunk skills section by skill categories."""
        chunks = []
        
        # Look for skill categories or bullet points
        skill_categories = re.split(r'\n\s*[\*\-•]\s*', text)
        
        current_chunk = ""
        chunk_count = 0
        
        for category in skill_categories:
            category = category.strip()
            if not category:
                continue
            
            # If adding this category would exceed max words, create a new chunk
            combined = (current_chunk + "\n• " + category).strip()
            if len(combined.split()) > self.max_words and len(current_chunk.split()) > 20:
                chunks.append({
                    'text': current_chunk.strip(),
                    'heading': f"{heading} (Part {chunk_count + 1})" if chunk_count > 0 else heading,
                    'type': 'skills',
                    'word_count': len(current_chunk.split()),
                    'parent_heading': heading
                })
                chunk_count += 1
                current_chunk = "• " + category
            else:
                current_chunk = combined
        
        # Add the last chunk
        if current_chunk and len(current_chunk.split()) > 10:
            chunks.append({
                'text': current_chunk.strip(),
                'heading': f"{heading} (Part {chunk_count + 1})" if chunk_count > 0 else heading,
                'type': 'skills',
                'word_count': len(current_chunk.split()),
                'parent_heading': heading
            })
        
        return chunks

    def _chunk_general_section(self, text: str, heading: str) -> List[Dict[str, Any]]:
        """Chunk general sections by paragraphs and size."""
        return self._split_by_size(text, self.max_words, heading)

    def _split_by_size(self, text: str, max_words: int, heading: str = "Content") -> List[Dict[str, Any]]:
        """Split text by size while respecting paragraph boundaries."""
        chunks = []
        paragraphs = text.split('\n\n')
        
        current_chunk = ""
        chunk_count = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Check if adding this paragraph would exceed max words
            combined = (current_chunk + "\n\n" + paragraph).strip()
            if len(combined.split()) > max_words and len(current_chunk.split()) > 20:
                chunks.append({
                    'text': current_chunk.strip(),
                    'heading': f"{heading} (Part {chunk_count + 1})" if chunk_count > 0 else heading,
                    'type': 'content',
                    'word_count': len(current_chunk.split()),
                    'parent_heading': heading
                })
                chunk_count += 1
                current_chunk = paragraph
            else:
                current_chunk = combined
        
        # Add the last chunk
        if current_chunk and len(current_chunk.split()) > 10:
            chunks.append({
                'text': current_chunk.strip(),
                'heading': f"{heading} (Part {chunk_count + 1})" if chunk_count > 0 else heading,
                'type': 'content',
                'word_count': len(current_chunk.split()),
                'parent_heading': heading
            })
        
        return chunks

    def chunk_markdown(self, text: str) -> List[Dict[str, Any]]:
        """Smart chunking for general Markdown with headers."""
        # Use the same improved logic as CV chunking
        return self.chunk_cv_markdown(text) 