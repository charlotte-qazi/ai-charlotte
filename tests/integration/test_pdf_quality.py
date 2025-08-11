#!/usr/bin/env python3
"""
PDF parsing quality test with Markdown reference comparison.
Run: pytest tests/integration/test_pdf_quality.py -v -s

This test compares PDF extraction against a Markdown reference file to measure:
- Text similarity (character and word level)
- Content preservation
- Extraction completeness
"""

import re
from pathlib import Path
from difflib import SequenceMatcher

import pytest

from backend.services.ingestion.loader import PDFLoader


def clean_markdown_for_comparison(text: str) -> str:
    """Clean Markdown text for comparison with PDF extraction."""
    # Remove Markdown formatting
    text = re.sub(r'#{1,6}\s+', '', text)  # Remove headers
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Remove bold **text**
    text = re.sub(r'\*(.*?)\*', r'\1', text)  # Remove italic *text*
    text = re.sub(r'`(.*?)`', r'\1', text)  # Remove inline code
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  # Remove links, keep text
    text = re.sub(r'^[-*+]\s+', '', text, flags=re.MULTILINE)  # Remove bullet points
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)  # Remove numbered lists
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)  # Remove blockquotes
    text = re.sub(r'---+', '', text)  # Remove horizontal rules
    
    return text


def normalize_text(text: str) -> str:
    """Normalize text for comparison by removing extra whitespace and standardizing."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    # Convert to lowercase for case-insensitive comparison
    text = text.lower()
    return text


def calculate_similarity(text1: str, text2: str) -> dict:
    """Calculate various similarity metrics between two texts."""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)
    
    # Character-level similarity
    char_similarity = SequenceMatcher(None, norm1, norm2).ratio()
    
    # Word-level similarity
    words1 = set(norm1.split())
    words2 = set(norm2.split())
    word_intersection = len(words1.intersection(words2))
    word_union = len(words1.union(words2))
    word_similarity = word_intersection / word_union if word_union > 0 else 0
    
    # Length comparison
    len1, len2 = len(norm1), len(norm2)
    length_ratio = min(len1, len2) / max(len1, len2) if max(len1, len2) > 0 else 0
    
    # Word count comparison
    wc1, wc2 = len(norm1.split()), len(norm2.split())
    word_count_ratio = min(wc1, wc2) / max(wc1, wc2) if max(wc1, wc2) > 0 else 0
    
    return {
        "character_similarity": char_similarity,
        "word_similarity": word_similarity,
        "length_ratio": length_ratio,
        "word_count_ratio": word_count_ratio,
        "extracted_chars": len1,
        "reference_chars": len2,
        "extracted_words": wc1,
        "reference_words": wc2,
    }


def find_missing_content(reference: str, extracted: str, min_length: int = 20) -> list:
    """Find significant chunks of text that are missing from extraction."""
    ref_norm = normalize_text(reference)
    ext_norm = normalize_text(extracted)
    
    # Split reference into sentences/chunks
    chunks = re.split(r'[.!?]+', ref_norm)
    missing_chunks = []
    
    for chunk in chunks:
        chunk = chunk.strip()
        if len(chunk) >= min_length and chunk not in ext_norm:
            missing_chunks.append(chunk)
    
    return missing_chunks[:5]  # Return first 5 missing chunks


def test_pdf_extraction_quality():
    """Test PDF extraction quality against Markdown reference."""
    pdf_path = Path("data/raw/cv.pdf")
    md_reference_path = Path("data/raw/cv.md")
    
    # Skip if files don't exist
    if not pdf_path.exists():
        pytest.skip(f"PDF file not found: {pdf_path}")
    if not md_reference_path.exists():
        pytest.skip(f"Markdown reference not found: {md_reference_path}. Create this file with your CV content in Markdown format.")
    
    print(f"\n🔍 Testing PDF extraction quality against Markdown reference")
    print("=" * 70)
    
    # Load Markdown reference
    with md_reference_path.open("r", encoding="utf-8") as f:
        md_text = f.read()
    
    # Clean Markdown for comparison
    reference_text = clean_markdown_for_comparison(md_text)
    
    print(f"📄 Markdown reference loaded: {len(md_text):,} chars (raw), {len(reference_text):,} chars (cleaned)")
    print(f"   📏 Words: {len(reference_text.split()):,}")
    
    # Extract text from PDF
    loader = PDFLoader(pdf_path)
    extracted_text = loader.load_text()
    
    print(f"📄 PDF text extracted: {len(extracted_text):,} chars, {len(extracted_text.split()):,} words")
    
    # Calculate similarity metrics
    metrics = calculate_similarity(reference_text, extracted_text)
    
    print(f"\n📊 Similarity Metrics:")
    print(f"   Character similarity: {metrics['character_similarity']:.1%}")
    print(f"   Word similarity: {metrics['word_similarity']:.1%}")
    print(f"   Length ratio: {metrics['length_ratio']:.1%}")
    print(f"   Word count ratio: {metrics['word_count_ratio']:.1%}")
    
    # Quality thresholds (may be lower due to PDF extraction vs clean Markdown)
    min_char_similarity = 0.75  # 75% character similarity (lower due to formatting differences)
    min_word_similarity = 0.85  # 85% word similarity
    min_length_ratio = 0.80     # 80% length preservation (PDF may have spacing issues)
    min_word_ratio = 0.90       # 90% word count preservation
    
    print(f"\n✅ Quality Thresholds:")
    print(f"   Character similarity: {metrics['character_similarity']:.1%} {'✅' if metrics['character_similarity'] >= min_char_similarity else '❌'} (>= {min_char_similarity:.1%})")
    print(f"   Word similarity: {metrics['word_similarity']:.1%} {'✅' if metrics['word_similarity'] >= min_word_similarity else '❌'} (>= {min_word_similarity:.1%})")
    print(f"   Length ratio: {metrics['length_ratio']:.1%} {'✅' if metrics['length_ratio'] >= min_length_ratio else '❌'} (>= {min_length_ratio:.1%})")
    print(f"   Word count ratio: {metrics['word_count_ratio']:.1%} {'✅' if metrics['word_count_ratio'] >= min_word_ratio else '❌'} (>= {min_word_ratio:.1%})")
    
    # Find missing content
    missing_chunks = find_missing_content(reference_text, extracted_text)
    if missing_chunks:
        print(f"\n⚠️  Potentially missing content ({len(missing_chunks)} chunks):")
        for i, chunk in enumerate(missing_chunks, 1):
            print(f"   {i}. {chunk[:100]}...")
    else:
        print(f"\n✅ No significant missing content detected")
    
    # Show sample comparison
    ref_sample = reference_text[:200]
    ext_sample = extracted_text[:200]
    print(f"\n📖 Sample Comparison (first 200 chars):")
    print(f"Markdown: {repr(ref_sample)}")
    print(f"PDF:      {repr(ext_sample)}")
    
    # Show Markdown preview
    print(f"\n📝 Raw Markdown preview (first 300 chars):")
    print(f"{repr(md_text[:300])}...")
    
    # Assertions for quality gates
    assert metrics['character_similarity'] >= min_char_similarity, f"Character similarity too low: {metrics['character_similarity']:.1%} < {min_char_similarity:.1%}"
    assert metrics['word_similarity'] >= min_word_similarity, f"Word similarity too low: {metrics['word_similarity']:.1%} < {min_word_similarity:.1%}"
    assert metrics['length_ratio'] >= min_length_ratio, f"Length ratio too low: {metrics['length_ratio']:.1%} < {min_length_ratio:.1%}"
    assert metrics['word_count_ratio'] >= min_word_ratio, f"Word count ratio too low: {metrics['word_count_ratio']:.1%} < {min_word_ratio:.1%}"
    
    print(f"\n🎉 PDF extraction quality test passed!")


if __name__ == "__main__":
    test_pdf_extraction_quality() 