#!/usr/bin/env python3
"""
Improved document processing with better chunking for Charlotte's CV format.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

from backend.services.ingestion.loader import PDFLoader


def simple_cv_chunker(text: str, max_words: int = 120) -> List[Dict[str, Any]]:
    """
    Simple but effective chunker specifically for Charlotte's CV format.
    """
    chunks = []
    
    # Clean the text
    text = re.sub(r'\|\s*\|\s*', ' ', text)  # Remove table formatting
    text = re.sub(r'\|\s*:\-+\s*\|\s*', ' ', text)
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    
    # Split by major sections: --- and **Section Name**
    sections = re.split(r'(?:\n\s*---\s*\n|\n\s*\*\*([^*]+)\*\*\s*\n)', text)
    
    current_heading = "Profile"
    
    for i, section in enumerate(sections):
        section = section.strip()
        if not section:
            continue
        
        # Check if this is a heading (short text with key words)
        words = section.split()
        if (len(words) <= 5 and 
            any(keyword in section.lower() for keyword in 
                ['experience', 'education', 'skills', 'professional', 'technical'])):
            current_heading = section
            continue
        
        if len(words) < 10:  # Skip very short sections
            continue
        
        # Now chunk this section
        if 'experience' in current_heading.lower() or 'professional' in current_heading.lower():
            section_chunks = chunk_experience_section(section, current_heading, max_words)
        elif 'education' in current_heading.lower():
            section_chunks = chunk_education_section(section, current_heading, max_words)
        elif 'skills' in current_heading.lower() or 'technical' in current_heading.lower():
            section_chunks = chunk_skills_section(section, current_heading, max_words)
        else:
            section_chunks = chunk_general_section(section, current_heading, max_words)
        
        chunks.extend(section_chunks)
    
    return chunks


def chunk_experience_section(text: str, heading: str, max_words: int) -> List[Dict[str, Any]]:
    """Chunk experience by individual jobs."""
    chunks = []
    
    # Split by job entries - look for **Job Title** or company patterns
    job_entries = []
    
    # Method 1: Split by **Job Title** pattern
    job_parts = re.split(r'\n\s*\*\*([^*]+)\*\*\s*\n', text)
    
    current_job = ""
    current_title = ""
    
    for i, part in enumerate(job_parts):
        part = part.strip()
        if not part:
            continue
        
        # If this looks like a job title (short, contains job-related words)
        if (len(part.split()) <= 8 and 
            any(word in part.lower() for word in 
                ['engineer', 'manager', 'consultant', 'intern', 'student', 'general', 'senior'])):
            # Save previous job if it exists
            if current_job and len(current_job.split()) > 15:
                job_entries.append({
                    'text': current_job.strip(),
                    'title': current_title or f"{heading} Job"
                })
            
            current_title = part
            current_job = ""
        else:
            current_job += "\n" + part if current_job else part
    
    # Add the last job
    if current_job and len(current_job.split()) > 15:
        job_entries.append({
            'text': current_job.strip(),
            'title': current_title or f"{heading} Job"
        })
    
    # If no jobs found, split by company/organization patterns
    if not job_entries:
        # Look for lines that contain company names and dates
        lines = text.split('\n')
        current_job = ""
        current_company = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line looks like "Company Name, Location | Date"
            if ('|' in line and 
                any(char.isdigit() for char in line) and  # Contains dates
                len(line.split()) <= 12):  # Reasonable company line length
                
                # Save previous job
                if current_job and len(current_job.split()) > 10:
                    job_entries.append({
                        'text': current_job.strip(),
                        'title': current_company or f"{heading} Position"
                    })
                
                current_company = line.split('|')[0].strip() if '|' in line else line
                current_job = line
            else:
                current_job += "\n" + line if current_job else line
        
        # Add last job
        if current_job and len(current_job.split()) > 10:
            job_entries.append({
                'text': current_job.strip(),
                'title': current_company or f"{heading} Position"
            })
    
    # Convert to chunks
    for i, job in enumerate(job_entries):
        words = job['text'].split()
        if len(words) < 8:
            continue
        
        # If job is too long, split it
        if len(words) > max_words:
            # Split by paragraphs or bullet points
            sub_chunks = split_text_smartly(job['text'], max_words, job['title'])
            chunks.extend(sub_chunks)
        else:
            chunks.append({
                'text': job['text'],
                'heading': job['title'],
                'type': 'job_experience',
                'word_count': len(words),
                'parent_heading': heading
            })
    
    return chunks


def chunk_education_section(text: str, heading: str, max_words: int) -> List[Dict[str, Any]]:
    """Chunk education section."""
    chunks = []
    
    # Split by degree/institution patterns
    edu_parts = re.split(r'\n\s*\*\*([^*]+)\*\*\s*\n', text)
    
    current_edu = ""
    current_degree = ""
    
    for part in edu_parts:
        part = part.strip()
        if not part:
            continue
        
        # If this looks like a degree/qualification
        if (len(part.split()) <= 10 and 
            any(word in part.lower() for word in 
                ['degree', 'bsc', 'msc', 'ba', 'ma', 'phd', 'diploma', 'certificate', 'class'])):
            
            # Save previous education
            if current_edu and len(current_edu.split()) > 8:
                chunks.append({
                    'text': current_edu.strip(),
                    'heading': current_degree or f"{heading} Qualification",
                    'type': 'education',
                    'word_count': len(current_edu.split()),
                    'parent_heading': heading
                })
            
            current_degree = part
            current_edu = ""
        else:
            current_edu += "\n" + part if current_edu else part
    
    # Add last education entry
    if current_edu and len(current_edu.split()) > 8:
        chunks.append({
            'text': current_edu.strip(),
            'heading': current_degree or f"{heading} Qualification",
            'type': 'education',
            'word_count': len(current_edu.split()),
            'parent_heading': heading
        })
    
    # If no education entries found, treat as single chunk
    if not chunks and len(text.split()) > 10:
        chunks.append({
            'text': text,
            'heading': heading,
            'type': 'education',
            'word_count': len(text.split()),
            'parent_heading': heading
        })
    
    return chunks


def chunk_skills_section(text: str, heading: str, max_words: int) -> List[Dict[str, Any]]:
    """Chunk skills by categories."""
    chunks = []
    
    # Split by bullet points or skill categories
    skill_parts = re.split(r'\n\s*[\*\-•]\s*', text)
    
    current_chunk = ""
    chunk_count = 0
    
    for part in skill_parts:
        part = part.strip()
        if not part:
            continue
        
        # Add bullet point back
        skill_text = "• " + part
        combined = (current_chunk + "\n" + skill_text).strip()
        
        if len(combined.split()) > max_words and len(current_chunk.split()) > 20:
            chunks.append({
                'text': current_chunk.strip(),
                'heading': f"{heading}" + (f" (Part {chunk_count + 1})" if chunk_count > 0 else ""),
                'type': 'skills',
                'word_count': len(current_chunk.split()),
                'parent_heading': heading
            })
            chunk_count += 1
            current_chunk = skill_text
        else:
            current_chunk = combined
    
    # Add final chunk
    if current_chunk and len(current_chunk.split()) > 5:
        chunks.append({
            'text': current_chunk.strip(),
            'heading': f"{heading}" + (f" (Part {chunk_count + 1})" if chunk_count > 0 else ""),
            'type': 'skills',
            'word_count': len(current_chunk.split()),
            'parent_heading': heading
        })
    
    return chunks


def chunk_general_section(text: str, heading: str, max_words: int) -> List[Dict[str, Any]]:
    """Chunk general content."""
    return split_text_smartly(text, max_words, heading)


def split_text_smartly(text: str, max_words: int, heading: str) -> List[Dict[str, Any]]:
    """Split text by paragraphs and bullet points while respecting word limits."""
    chunks = []
    
    # Split by paragraphs first
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    if not paragraphs:
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    current_chunk = ""
    chunk_count = 0
    
    for paragraph in paragraphs:
        combined = (current_chunk + "\n\n" + paragraph).strip()
        
        if len(combined.split()) > max_words and len(current_chunk.split()) > 20:
            chunks.append({
                'text': current_chunk.strip(),
                'heading': f"{heading}" + (f" (Part {chunk_count + 1})" if chunk_count > 0 else ""),
                'type': 'content',
                'word_count': len(current_chunk.split()),
                'parent_heading': heading
            })
            chunk_count += 1
            current_chunk = paragraph
        else:
            current_chunk = combined
    
    # Add final chunk
    if current_chunk and len(current_chunk.split()) > 8:
        chunks.append({
            'text': current_chunk.strip(),
            'heading': f"{heading}" + (f" (Part {chunk_count + 1})" if chunk_count > 0 else ""),
            'type': 'content',
            'word_count': len(current_chunk.split()),
            'parent_heading': heading
        })
    
    return chunks


def write_jsonl(output_path: Path, records: List[Dict[str, Any]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def process_document_improved(
    input_path: Path,
    output_jsonl: Path,
    source_label: str,
    max_words: int = 120,
) -> None:
    print(f"🔍 Processing with improved chunking: {input_path.name}")
    print(f"🎯 Max words per chunk: {max_words}")
    print("=" * 60)
    
    # Load content
    if input_path.suffix.lower() == '.pdf':
        loader = PDFLoader(input_path)
        content = loader.load_text()
        source_format = "pdf"
    elif input_path.suffix.lower() in ['.md', '.markdown']:
        with input_path.open("r", encoding="utf-8") as f:
            content = f.read()
        source_format = "markdown"
    else:
        raise ValueError(f"Unsupported file format: {input_path.suffix}")
    
    print(f"📄 Content loaded: {len(content):,} characters")
    
    # Chunk the content
    chunks = simple_cv_chunker(content, max_words)
    
    print(f"🧩 Created {len(chunks)} chunks")
    print(f"\n📋 Chunk breakdown:")
    total_words = 0
    for i, chunk in enumerate(chunks):
        heading = chunk.get('heading', 'Unknown')
        word_count = chunk.get('word_count', 0)
        chunk_type = chunk.get('type', 'content')
        total_words += word_count
        print(f"   {i:2}: '{heading}' ({word_count} words, {chunk_type})")
    
    avg_words = total_words / len(chunks) if chunks else 0
    print(f"\n📊 Average chunk size: {avg_words:.1f} words")
    
    # Convert to JSONL
    records: List[Dict[str, Any]] = []
    for index, chunk in enumerate(chunks):
        record = {
            "id": f"{input_path.stem}-{index}",
            "chunk_index": index,
            "text": chunk['text'],
            "source": source_label,
            "heading": chunk.get('heading', 'Unknown'),
            "chunk_type": chunk.get('type', 'content'),
            "word_count": chunk.get('word_count', 0),
            "parent_heading": chunk.get('parent_heading', ''),
            "metadata": {
                "filename": input_path.name,
                "path": str(input_path),
                "improved_chunking": True,
                "source_format": source_format,
                "max_words": max_words
            },
        }
        records.append(record)
    
    # Write output
    write_jsonl(output_jsonl, records)
    print(f"\n✅ Saved {len(records)} chunks to {output_jsonl}")
    
    # Show samples
    print(f"\n📖 Sample chunks:")
    for i, record in enumerate(records[:3]):
        print(f"\n--- Chunk {i}: {record['heading']} ({record['word_count']} words) ---")
        preview = record['text'].replace('\n', ' ')[:150]
        print(f"{preview}...")


def main() -> None:
    parser = argparse.ArgumentParser(description="Improved document processing")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--max-words", type=int, default=120)
    parser.add_argument("--source-label", type=str, default=None)

    args = parser.parse_args()
    
    if args.output is None:
        args.output = Path("data/processed") / f"{args.input.stem}_improved_chunks.jsonl"
    
    if args.source_label is None:
        args.source_label = args.input.stem
    
    try:
        process_document_improved(
            input_path=args.input,
            output_jsonl=args.output,
            source_label=args.source_label,
            max_words=args.max_words,
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main() 