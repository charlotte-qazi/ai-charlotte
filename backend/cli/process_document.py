#!/usr/bin/env python3
"""
Unified document processing with smart chunking.
Supports PDF and Markdown inputs with intelligent semantic chunking.

Usage:
python -m backend.cli.process_document --input data/raw/cv.pdf --output data/processed/cv_chunks.jsonl
python -m backend.cli.process_document --input data/raw/cv.md --output data/processed/cv_chunks.jsonl
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from backend.services.ingestion.loader import PDFLoader
from backend.services.chunking.smart_chunker import SmartChunker


def write_jsonl(output_path: Path, records: List[Dict[str, Any]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def process_document(
    input_path: Path,
    output_jsonl: Path,
    source_label: str,
    target_words: int = 200,
    max_words: int = 350,
) -> None:
    print(f"🔍 Processing document with smart chunking: {input_path.name}")
    print(f"🎯 Target: {target_words} words per chunk, Max: {max_words} words")
    print("=" * 60)
    
    # Determine input type and load content
    if input_path.suffix.lower() == '.pdf':
        print(f"📄 Loading PDF...")
        loader = PDFLoader(input_path)
        content = loader.load_text()
        source_format = "pdf"
        
        # For PDF, use CV-specific chunking (handles formatting issues better)
        chunker = SmartChunker(target_words=target_words, max_words=max_words)
        chunks = chunker.chunk_cv_markdown(content)
        
    elif input_path.suffix.lower() in ['.md', '.markdown']:
        print(f"📝 Loading Markdown...")
        with input_path.open("r", encoding="utf-8") as f:
            content = f.read()
        source_format = "markdown"
        
        # Detect if this is a CV format or regular Markdown
        if any(pattern in content for pattern in ['**Professional Experience**', '**Senior', '**Education**']):
            print(f"🎯 Detected CV format, using CV-specific chunking...")
            chunker = SmartChunker(target_words=target_words, max_words=max_words)
            chunks = chunker.chunk_cv_markdown(content)
        else:
            print(f"📋 Using standard Markdown chunking...")
            chunker = SmartChunker(target_words=target_words, max_words=max_words)
            chunks = chunker.chunk_markdown(content)
    else:
        raise ValueError(f"Unsupported file format: {input_path.suffix}")
    
    print(f"📄 Content loaded: {len(content):,} characters")
    print(f"🧩 Created {len(chunks)} smart chunks")
    
    # Show chunk breakdown
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
    
    # Convert to JSONL format
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
                "smart_chunking": True,
                "source_format": source_format,
                "target_words": target_words,
                "max_words": max_words
            },
        }
        records.append(record)
    
    # Write output
    write_jsonl(output_jsonl, records)
    
    print(f"\n✅ Saved {len(records)} smart chunks to {output_jsonl}")
    
    # Show sample chunks
    print(f"\n📖 Sample chunks:")
    for i, record in enumerate(records[:3]):
        print(f"\n--- Chunk {i}: {record['heading']} ({record['word_count']} words) ---")
        preview = record['text'].replace('\n', ' ')[:150]
        print(f"{preview}...")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Process documents (PDF/Markdown) with smart semantic chunking"
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to input document (PDF or Markdown)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Path to output JSONL (auto-generated if not specified)",
    )
    parser.add_argument(
        "--target-words",
        type=int,
        default=200,
        help="Target words per chunk (default: 200)",
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=350,
        help="Maximum words per chunk (default: 350)",
    )
    parser.add_argument(
        "--source-label",
        type=str,
        default=None,
        help="Source label to attach to chunks (auto-generated if not specified)",
    )

    args = parser.parse_args()
    
    # Auto-generate output path if not specified
    if args.output is None:
        args.output = Path("data/processed") / f"{args.input.stem}_chunks.jsonl"
    
    # Auto-generate source label if not specified
    if args.source_label is None:
        args.source_label = args.input.stem
    
    try:
        process_document(
            input_path=args.input,
            output_jsonl=args.output,
            source_label=args.source_label,
            target_words=args.target_words,
            max_words=args.max_words,
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main() 