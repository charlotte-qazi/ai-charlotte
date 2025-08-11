#!/usr/bin/env python3
"""
Simple CLI tool to process any CV (PDF or Markdown) into chunks.
Works with any CV format - not specific to Charlotte's CV.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any

from backend.services.chunking.cv_chunker import CVChunker
from backend.services.ingestion.loader import PDFLoader


def load_document(input_path: Path) -> str:
    """Load document content based on file type."""
    if input_path.suffix.lower() == '.pdf':
        loader = PDFLoader(input_path)
        return loader.load_text()
    elif input_path.suffix.lower() in ['.md', '.markdown', '.txt']:
        with input_path.open('r', encoding='utf-8') as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file format: {input_path.suffix}")


def write_jsonl(chunks: list, output_path: Path) -> None:
    """Write chunks to JSONL file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with output_path.open('w', encoding='utf-8') as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + '\n')


def process_cv(
    input_path: Path,
    output_path: Path,
    source_label: str,
    target_words: int = 100,
    max_words: int = 150
) -> Dict[str, Any]:
    """Process a CV and return statistics."""
    
    print(f"🔍 Processing: {input_path}")
    
    # Load document
    try:
        content = load_document(input_path)
        print(f"📄 Loaded {len(content)} characters")
    except Exception as e:
        print(f"❌ Failed to load document: {e}")
        return {}
    
    # Create chunker and process
    chunker = CVChunker(target_words=target_words, max_words=max_words)
    chunks = chunker.chunk_cv(content)
    
    if not chunks:
        print("⚠️  No chunks generated")
        return {}
    
    # Convert to JSONL format
    jsonl_records = []
    for i, chunk in enumerate(chunks):
        record = {
            "id": f"{source_label}-{i}",
            "chunk_index": i,
            "text": chunk["text"],
            "source": source_label,
            "heading": chunk["heading"],
            "chunk_type": chunk["chunk_type"],
            "word_count": chunk["word_count"],
            "parent_heading": chunk.get("parent_heading", ""),
            "metadata": {
                "filename": input_path.name,
                "target_words": target_words,
                "max_words": max_words,
                "generic_cv_chunker": True
            }
        }
        jsonl_records.append(record)
    
    # Write to file
    write_jsonl(jsonl_records, output_path)
    
    # Generate statistics
    total_words = sum(record["word_count"] for record in jsonl_records)
    chunk_types = {}
    for record in jsonl_records:
        chunk_type = record["chunk_type"]
        chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
    
    stats = {
        "input_file": str(input_path),
        "output_file": str(output_path),
        "source_label": source_label,
        "total_chunks": len(jsonl_records),
        "total_words": total_words,
        "average_words": round(total_words / len(jsonl_records), 1),
        "chunk_types": chunk_types,
        "config": {
            "target_words": target_words,
            "max_words": max_words
        }
    }
    
    return stats


def print_stats(stats: Dict[str, Any]) -> None:
    """Print processing statistics."""
    if not stats:
        return
    
    print(f"\n✅ Processing Complete!")
    print(f"📊 Results: {stats['total_chunks']} chunks, {stats['total_words']} total words")
    print(f"📈 Average: {stats['average_words']} words per chunk")
    print("\n📋 Chunk types:")
    
    for chunk_type, count in stats["chunk_types"].items():
        print(f"   {chunk_type}: {count} chunks")
    
    print(f"\n💾 Saved to: {stats['output_file']}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Process any CV (PDF or Markdown) into semantic chunks"
    )
    
    parser.add_argument(
        "input_file",
        type=Path,
        help="Input CV file (PDF or Markdown)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output JSONL file (default: data/processed/{input_stem}_chunks.jsonl)"
    )
    
    parser.add_argument(
        "-s", "--source",
        type=str,
        help="Source label for chunks (default: input filename)"
    )
    
    parser.add_argument(
        "--target-words",
        type=int,
        default=100,
        help="Target words per chunk (default: 100)"
    )
    
    parser.add_argument(
        "--max-words",
        type=int,
        default=150,
        help="Maximum words per chunk (default: 150)"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not args.input_file.exists():
        print(f"❌ Input file not found: {args.input_file}")
        return 1
    
    # Set defaults
    output_path = args.output or Path("data/processed") / f"{args.input_file.stem}_chunks.jsonl"
    source_label = args.source or args.input_file.stem
    
    # Process the CV
    try:
        stats = process_cv(
            input_path=args.input_file,
            output_path=output_path,
            source_label=source_label,
            target_words=args.target_words,
            max_words=args.max_words
        )
        
        print_stats(stats)
        return 0
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main()) 