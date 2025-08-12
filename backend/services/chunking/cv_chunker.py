"""
AI Charlotte - CV Chunking Service
Copyright (c) 2025 Charlotte Qazi

Simple, generic CV chunker that works with any CV format.
Focuses on semantic sections and reasonable chunk sizes.

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

import re
from typing import List, Dict, Any


class CVChunker:
    """
    Simple CV chunker that works with any CV format.
    Automatically detects sections and creates reasonable chunks.
    """
    
    def __init__(self, target_words: int = 100, max_words: int = 150):
        self.target_words = target_words
        self.max_words = max_words
        self.min_words = 15
    
    def chunk_cv(self, text: str) -> List[Dict[str, Any]]:
        """
        Chunk a CV into semantic sections with reasonable sizes.
        Works with any CV format - PDF or Markdown.
        """
        # Clean the text first
        text = self._clean_text(text)
        
        # Try to split into sections
        sections = self._split_into_sections(text)
        
        # Process each section
        chunks = []
        for section in sections:
            section_chunks = self._chunk_section(section)
            chunks.extend(section_chunks)
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text from PDFs or markdown."""
        # Remove table formatting (common in markdown CVs)
        text = re.sub(r'\|[^|\n]*\|', ' ', text)
        text = re.sub(r'\|\s*:?-+:?\s*\|', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        return text.strip()
    
    def _split_into_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Split CV into logical sections.
        Works with various CV formats and styles.
        """
        sections = []
        
        # First, try to find common CV section headers (case-insensitive)
        common_sections = [
            'Professional Experience', 'Work Experience', 'Experience', 
            'Technical Skills', 'Skills', 'Core Competencies',
            'Education', 'Academic Background', 'Qualifications',
            'Publications', 'Publications & Presentations', 
            'Projects', 'Key Projects', 'Leadership', 'Volunteering'
        ]
        
        # Look for these section headers in the text
        section_markers = []
        for section_name in common_sections:
            pattern = r'\b' + re.escape(section_name) + r'\b'
            for match in re.finditer(pattern, text, re.IGNORECASE):
                section_markers.append({
                    'start': match.start(),
                    'end': match.end(),
                    'heading': match.group(),
                    'type': 'text_header'
                })
        
        # Also try regex patterns for formatted sections
        section_patterns = [
            # Markdown headers
            (r'\n\s*#{1,3}\s*([^\n]+)\n', 'header'),
            # Bold section titles
            (r'\n\s*\*\*([^*\n]+)\*\*\s*\n', 'bold'),
            # Underlined sections (common in text CVs)
            (r'\n\s*([A-Z\s]{3,})\s*\n\s*[-=]{3,}\s*\n', 'underlined'),
            # All caps sections
            (r'\n\s*([A-Z\s]{8,})\s*\n', 'caps'),
            # Horizontal rules (section separators)
            (r'\n\s*[-=*]{3,}\s*\n', 'separator'),
        ]
        
        # Add regex-based section markers
        for pattern, marker_type in section_patterns:
            for match in re.finditer(pattern, text):
                heading = ""
                if marker_type != 'separator':
                    heading = match.group(1).strip() if match.groups() else ""
                
                section_markers.append({
                    'start': match.start(),
                    'end': match.end(),
                    'heading': heading,
                    'type': marker_type
                })
        
        # Sort all markers by position
        section_markers.sort(key=lambda x: x['start'])  # type: ignore
        
        # Extract sections between markers
        current_pos = 0
        current_heading = "Profile"
        
        for marker in section_markers:
            # Extract text before this marker
            if marker['start'] > current_pos:
                section_text = text[current_pos:marker['start']].strip()
                if section_text and len(section_text.split()) > 10:
                    sections.append({
                        'text': section_text,
                        'heading': current_heading,
                        'type': self._classify_section(current_heading)
                    })
            
            # Update heading if this marker has one
            if marker['heading']:
                current_heading = marker['heading']
            
            current_pos = marker['end']
        
        # Add final section
        if current_pos < len(text):
            section_text = text[current_pos:].strip()
            if section_text and len(section_text.split()) > 10:
                sections.append({
                    'text': section_text,
                    'heading': current_heading,
                    'type': self._classify_section(current_heading)
                })
        
        return sections
    
    def _classify_section(self, heading: str) -> str:
        """Classify what type of section this is based on heading."""
        heading_lower = heading.lower()
        
        # Experience keywords
        if any(kw in heading_lower for kw in [
            'experience', 'work', 'career', 'employment', 'professional', 
            'positions', 'roles', 'history'
        ]):
            return 'experience'
        
        # Education keywords  
        elif any(kw in heading_lower for kw in [
            'education', 'qualifications', 'academic', 'degree', 'university',
            'college', 'school', 'certification', 'training'
        ]):
            return 'education'
        
        # Skills keywords
        elif any(kw in heading_lower for kw in [
            'skills', 'technical', 'expertise', 'competencies', 'technologies',
            'tools', 'languages', 'programming'
        ]):
            return 'skills'
        
        # Projects keywords
        elif any(kw in heading_lower for kw in [
            'projects', 'portfolio', 'work samples', 'achievements', 'publications', 'presentations', 'leadership', 'volunteering'
        ]):
            return 'projects'
        
        # Contact/Personal keywords
        elif any(kw in heading_lower for kw in [
            'contact', 'personal', 'details', 'information', 'summary', 'profile'
        ]):
            return 'personal'
        
        else:
            return 'general'
    
    def _chunk_section(self, section: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Chunk a section based on its type and content.
        Generic approach that works for any CV.
        """
        text = section['text']
        heading = section['heading']
        section_type = section['type']
        
        # For experience sections, try to split by jobs
        if section_type == 'experience':
            return self._chunk_experience(text, heading)
        
        # For education sections, try to split by degrees/institutions
        elif section_type == 'education':
            return self._chunk_education(text, heading)
        
        # For skills sections, split by categories or lists
        elif section_type == 'skills':
            return self._chunk_skills(text, heading)
        
        # For other sections, use paragraph-based chunking
        else:
            return self._chunk_by_paragraphs(text, heading, section_type)
    
    def _chunk_experience(self, text: str, heading: str) -> List[Dict[str, Any]]:
        """Chunk experience section by trying to identify individual jobs."""
        chunks = []
        
        # Look for job separators (dates, company names, job titles)
        job_patterns = [
            r'\n\s*\*\*([^*\n]+)\*\*',  # Bold job titles
            r'\n\s*([A-Z][^|\n]*)\s*\|\s*\d{4}',  # "Company | Date" format
            r'\n\s*\d{4}\s*[-–]\s*\d{4}',  # Date ranges
            r'\n\s*([A-Z][A-Za-z\s&,]+)\s*,\s*[A-Z]',  # "Company, Location" format
        ]
        
        # Try to split by job patterns
        split_points = []
        for pattern in job_patterns:
            for match in re.finditer(pattern, text):
                split_points.append(match.start())
        
        split_points = sorted(set(split_points))
        
        if len(split_points) > 1:
            # Split by jobs
            for i in range(len(split_points)):
                start = split_points[i]
                end = split_points[i + 1] if i + 1 < len(split_points) else len(text)
                job_text = text[start:end].strip()
                
                if len(job_text.split()) >= self.min_words:
                    # Extract job title from the text
                    job_title = self._extract_job_title(job_text)
                    
                    chunks.append({
                        'text': job_text,
                        'heading': job_title,
                        'chunk_type': 'experience',
                        'word_count': len(job_text.split()),
                        'parent_heading': heading
                    })
        else:
            # Fallback to paragraph chunking
            chunks = self._chunk_by_paragraphs(text, heading, 'experience')
        
        return chunks
    
    def _chunk_education(self, text: str, heading: str) -> List[Dict[str, Any]]:
        """Chunk education section by degrees or institutions."""
        chunks = []
        
        # Look for degree/institution patterns
        edu_patterns = [
            r'\n\s*\*\*([^*\n]+)\*\*',  # Bold degree names
            r'\n\s*([A-Z][^|\n]*University[^|\n]*)',  # University names
            r'\n\s*(Bachelor|Master|PhD|BSc|MSc|BA|MA)[^|\n]*',  # Degree types
        ]
        
        split_points = []
        for pattern in edu_patterns:
            for match in re.finditer(pattern, text):
                split_points.append(match.start())
        
        split_points = sorted(set(split_points))
        
        if len(split_points) > 1:
            # Split by education entries
            for i in range(len(split_points)):
                start = split_points[i]
                end = split_points[i + 1] if i + 1 < len(split_points) else len(text)
                edu_text = text[start:end].strip()
                
                if len(edu_text.split()) >= self.min_words:
                    edu_title = self._extract_education_title(edu_text)
                    
                    chunks.append({
                        'text': edu_text,
                        'heading': edu_title,
                        'chunk_type': 'education',
                        'word_count': len(edu_text.split()),
                        'parent_heading': heading
                    })
        else:
            # Single education chunk
            chunks.append({
                'text': text,
                'heading': heading,
                'chunk_type': 'education',
                'word_count': len(text.split()),
                'parent_heading': heading
            })
        
        return chunks
    
    def _chunk_skills(self, text: str, heading: str) -> List[Dict[str, Any]]:
        """Chunk skills section by categories or reasonable sizes."""
        # Split by bullet points or categories
        if any(marker in text for marker in ['•', '*', '-']):
            # Has bullet points
            skill_items = re.split(r'\n\s*[•*-]\s*', text)
            skill_items = [item.strip() for item in skill_items if item.strip()]
            
            # Group into reasonable chunks
            chunks = []
            current_chunk = ""
            chunk_count = 0
            
            for item in skill_items:
                combined = (current_chunk + "\n• " + item).strip()
                
                if len(combined.split()) > self.max_words and current_chunk:
                    chunks.append({
                        'text': current_chunk.strip(),
                        'heading': f"{heading} (Part {chunk_count + 1})" if chunk_count > 0 else heading,
                        'chunk_type': 'skills',
                        'word_count': len(current_chunk.split()),
                        'parent_heading': heading
                    })
                    chunk_count += 1
                    current_chunk = "• " + item
                else:
                    current_chunk = combined
            
            # Add final chunk
            if current_chunk:
                chunks.append({
                    'text': current_chunk.strip(),
                    'heading': f"{heading} (Part {chunk_count + 1})" if chunk_count > 0 else heading,
                    'chunk_type': 'skills',
                    'word_count': len(current_chunk.split()),
                    'parent_heading': heading
                })
            
            return chunks
        else:
            # No clear structure, use paragraph chunking
            return self._chunk_by_paragraphs(text, heading, 'skills')
    
    def _chunk_by_paragraphs(self, text: str, heading: str, chunk_type: str) -> List[Dict[str, Any]]:
        """Generic paragraph-based chunking for any section."""
        chunks = []
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        current_text = ""
        chunk_count = 0
        
        for paragraph in paragraphs:
            combined = (current_text + "\n\n" + paragraph).strip()
            
            if len(combined.split()) > self.max_words and len(current_text.split()) >= self.min_words:
                chunks.append({
                    'text': current_text.strip(),
                    'heading': f"{heading} (Part {chunk_count + 1})" if chunk_count > 0 else heading,
                    'chunk_type': chunk_type,
                    'word_count': len(current_text.split()),
                    'parent_heading': heading
                })
                chunk_count += 1
                current_text = paragraph
            else:
                current_text = combined
        
        # Add final chunk
        if current_text and len(current_text.split()) >= self.min_words:
            chunks.append({
                'text': current_text.strip(),
                'heading': f"{heading} (Part {chunk_count + 1})" if chunk_count > 0 else heading,
                'chunk_type': chunk_type,
                'word_count': len(current_text.split()),
                'parent_heading': heading
            })
        
        return chunks
    
    def _extract_job_title(self, job_text: str) -> str:
        """Extract a job title from job text."""
        lines = job_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line:
                # Look for bold titles
                bold_match = re.search(r'\*\*([^*]+)\*\*', line)
                if bold_match:
                    return bold_match.group(1).strip()
                
                # Look for company | date format
                if '|' in line and any(char.isdigit() for char in line):
                    company = line.split('|')[0].strip()
                    return company
                
                # First non-empty line as fallback
                if len(line.split()) <= 10:  # Reasonable title length
                    return line
        
        return "Position"
    
    def _extract_education_title(self, edu_text: str) -> str:
        """Extract education title from education text."""
        lines = edu_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line:
                # Look for bold titles
                bold_match = re.search(r'\*\*([^*]+)\*\*', line)
                if bold_match:
                    return bold_match.group(1).strip()
                
                # Look for degree patterns
                degree_match = re.search(r'(Bachelor|Master|PhD|BSc|MSc|BA|MA)[^|\n]*', line)
                if degree_match:
                    return degree_match.group(0).strip()
                
                # Look for university names
                if 'university' in line.lower() or 'college' in line.lower():
                    return line
                
                # First non-empty line as fallback
                if len(line.split()) <= 15:
                    return line
        
        return "Education" 