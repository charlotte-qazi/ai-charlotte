#!/usr/bin/env python3
"""
Integration test for PDF parsing quality.
Run: pytest tests/integration/test_pdf_parsing.py -v
Or: python -m pytest tests/integration/test_pdf_parsing.py -v
"""

import json
from pathlib import Path
from typing import Dict, List

import pytest

from backend.services.ingestion.loader import PDFLoader
from backend.services.chunking.chunker import TextChunker


def load_chunks_from_jsonl(jsonl_path: Path) -> List[Dict]:
    """Load chunks from JSONL file."""
    chunks = []
    if jsonl_path.exists():
        with jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                chunks.append(json.loads(line.strip()))
    return chunks


def test_pdf_parsing_quality():
    """Test PDF parsing quality with assertions."""
    pdf_path = Path("data/raw/cv.pdf")
    jsonl_path = Path("data/processed/cv_chunks.jsonl")
    
    # Skip if no PDF file
    if not pdf_path.exists():
        pytest.skip(f"PDF file not found: {pdf_path}")
    
    print(f"\n🔍 Testing PDF parsing for: {pdf_path.name}")
    print("=" * 60)
    
    # 1. Test PDF loading
    loader = PDFLoader(pdf_path)
    full_text = loader.load_text()
    pages = loader.load_text_by_page()
    
    print(f"✅ PDF loaded successfully")
    print(f"   📄 Pages: {len(pages)}")
    print(f"   📝 Total characters: {len(full_text):,}")
    print(f"   📏 Total words (approx): {len(full_text.split()):,}")
    
    # Assertions for PDF loading
    assert len(pages) > 0, "Should extract at least one page"
    assert len(full_text) > 100, "Should extract meaningful text content"
    assert len(full_text.split()) > 50, "Should extract reasonable word count"
    
    # 2. Test chunking
    chunker = TextChunker(max_chars=1200, overlap_chars=200)
    chunks = chunker.chunk(full_text)
    
    print(f"\n✅ Chunking completed")
    print(f"   🧩 Chunks created: {len(chunks)}")
    print(f"   📊 Avg chunk size: {sum(len(c) for c in chunks) // len(chunks):,} chars")
    print(f"   📏 Min chunk size: {min(len(c) for c in chunks):,} chars")
    print(f"   📏 Max chunk size: {max(len(c) for c in chunks):,} chars")
    
    # Assertions for chunking
    assert len(chunks) > 0, "Should create at least one chunk"
    assert all(len(chunk) <= 1200 for chunk in chunks), "All chunks should be within max size"
    assert all(len(chunk) > 0 for chunk in chunks), "All chunks should have content"
    
    # 3. Test JSONL output (if exists)
    if jsonl_path.exists():
        jsonl_chunks = load_chunks_from_jsonl(jsonl_path)
        print(f"\n✅ JSONL file found")
        print(f"   📁 File: {jsonl_path}")
        print(f"   🧩 Chunks in file: {len(jsonl_chunks)}")
        
        # Validate JSONL structure
        if jsonl_chunks:
            sample = jsonl_chunks[0]
            required_fields = ["id", "chunk_index", "text", "source", "metadata"]
            missing = [f for f in required_fields if f not in sample]
            if missing:
                print(f"   ⚠️  Missing fields: {missing}")
            else:
                print(f"   ✅ All required fields present")
            
            # Assertions for JSONL
            assert len(jsonl_chunks) == len(chunks), "JSONL should have same number of chunks"
            assert all(field in sample for field in required_fields), "Should have all required fields"
            assert sample["source"] == "cv", "Should have correct source label"
            assert "filename" in sample["metadata"], "Should have filename in metadata"
    
    # 4. Content quality checks
    print(f"\n📋 Content Quality Checks:")
    
    # Check for reasonable text extraction
    if len(full_text.strip()) < 100:
        print(f"   ⚠️  Very short text extracted ({len(full_text)} chars) - might be scanned PDF")
    else:
        print(f"   ✅ Reasonable text length extracted")
    
    # Check for excessive whitespace/formatting issues
    clean_text = " ".join(full_text.split())
    whitespace_ratio = (len(full_text) - len(clean_text)) / len(full_text)
    if whitespace_ratio > 0.3:
        print(f"   ⚠️  High whitespace ratio ({whitespace_ratio:.1%}) - formatting issues possible")
    else:
        print(f"   ✅ Clean text formatting ({whitespace_ratio:.1%} whitespace)")
    
    # Assertions for content quality
    assert len(full_text.strip()) >= 100, "Should extract meaningful content"
    assert whitespace_ratio < 0.5, "Whitespace ratio should be reasonable"
    
    # Check chunk overlap
    if len(chunks) > 1:
        overlaps = []
        for i in range(len(chunks) - 1):
            chunk1_end = chunks[i][-200:]  # Last 200 chars
            chunk2_start = chunks[i+1][:200]  # First 200 chars
            # Simple overlap check
            overlap_found = any(word in chunk2_start for word in chunk1_end.split()[-10:])
            overlaps.append(overlap_found)
        
        overlap_pct = sum(overlaps) / len(overlaps) * 100
        if overlap_pct > 50:
            print(f"   ✅ Good chunk overlap ({overlap_pct:.0f}% of transitions)")
        else:
            print(f"   ⚠️  Low chunk overlap ({overlap_pct:.0f}% of transitions)")
        
        # Assertion for overlap
        assert overlap_pct > 0, "Should have some overlap between chunks"
    
    # 5. Sample content preview
    print(f"\n📖 Sample Content (first 300 chars):")
    print("-" * 60)
    print(repr(full_text[:300]) + "...")
    print("-" * 60)
    
    if chunks:
        print(f"\n🧩 First Chunk (300 chars):")
        print("-" * 60)
        print(repr(chunks[0][:300]) + "...")
        print("-" * 60)
    
    print(f"\n🎉 Test completed successfully!")


if __name__ == "__main__":
    # Allow running directly for manual testing
    test_pdf_parsing_quality() 