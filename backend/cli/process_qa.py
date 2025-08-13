#!/usr/bin/env python3
"""
AI Charlotte - Q&A Processing CLI
Copyright (c) 2025 Charlotte Qazi

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any

from backend.services.chunking.qa_chunker import QAChunker


def load_qa_document(input_path: Path) -> str:
    """Load Q&A document content."""
    if input_path.suffix.lower() in ['.md', '.markdown', '.txt']:
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


def process_qa(
    input_path: Path,
    output_path: Path,
    source_label: str
) -> Dict[str, Any]:
    """Process Q&A document into chunks."""
    
    print(f"🔍 Processing: {input_path}")
    
    # Load document
    text = load_qa_document(input_path)
    print(f"📄 Loaded {len(text)} characters")
    
    # Initialize chunker
    chunker = QAChunker()
    
    # Process into chunks
    raw_chunks = chunker.chunk_qa(text)
    
    if not raw_chunks:
        print("❌ No Q&A pairs found. Make sure questions are marked with ## headers.")
        return {
            'chunks_generated': 0,
            'total_words': 0,
            'output_file': str(output_path)
        }
    
    # Add metadata and IDs
    chunks = []
    for i, chunk in enumerate(raw_chunks):
        chunk_id = f"{source_label}_qa_{i+1}"
        
        chunk_with_metadata = {
            'id': chunk_id,
            'text': chunk['text'],
            'source': source_label,
            'type': 'qa',
            'heading': chunk['heading'],
            'chunk_type': chunk['chunk_type'],
            'word_count': chunk['word_count'],
            'chunk_index': i,
            'metadata': {
                'question': chunk['question'],
                'answer': chunk['answer']
            }
        }
        
        chunks.append(chunk_with_metadata)
    
    # Write to JSONL
    write_jsonl(chunks, output_path)
    
    # Calculate stats
    total_words = sum(chunk['word_count'] for chunk in chunks)
    avg_words = total_words / len(chunks) if chunks else 0
    
    print(f"\n✅ Processing Complete!")
    print(f"📊 Results: {len(chunks)} Q&A pairs, {total_words} total words")
    print(f"📈 Average: {avg_words:.1f} words per Q&A pair")
    
    return {
        'chunks_generated': len(chunks),
        'total_words': total_words,
        'average_words': avg_words,
        'output_file': str(output_path),
        'sample_chunks': [
            {
                'question': chunk['metadata']['question'][:60] + '...' if len(chunk['metadata']['question']) > 60 else chunk['metadata']['question'],
                'words': chunk['word_count']
            }
            for chunk in chunks[:3]  # Show first 3 as samples
        ]
    }


def print_stats(stats: Dict[str, Any]) -> None:
    """Print processing statistics."""
    print(f"\n📋 Sample Q&A pairs:")
    for i, sample in enumerate(stats['sample_chunks'], 1):
        print(f"   {i}. {sample['question']} ({sample['words']} words)")
    
    print(f"\n💾 Saved to: {stats['output_file']}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Process Q&A markdown files into individual question chunks"
    )
    
    parser.add_argument(
        "input_file",
        type=Path,
        help="Input Q&A file (Markdown)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output JSONL file (default: data/processed/{input_stem}_qa_chunks.jsonl)"
    )
    
    parser.add_argument(
        "-s", "--source",
        type=str,
        help="Source label for chunks (default: input filename)"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not args.input_file.exists():
        print(f"❌ Input file not found: {args.input_file}")
        return 1
    
    # Set defaults
    output_path = args.output or Path("data/processed") / f"{args.input_file.stem}_qa_chunks.jsonl"
    source_label = args.source or args.input_file.stem
    
    # Process the Q&A file
    try:
        stats = process_qa(
            input_path=args.input_file,
            output_path=output_path,
            source_label=source_label
        )
        
        print_stats(stats)
        
        print(f"\n🚀 Ready for embedding! Use:")
        print(f"   python -m backend.cli.embed_and_upsert --input {output_path} --collection ai_charlotte")
        
        return 0
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main()) 