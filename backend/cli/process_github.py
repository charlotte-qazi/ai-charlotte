#!/usr/bin/env python3
"""
Process GitHub repositories: ingest, chunk, and save to JSONL.

Usage:
python -m backend.cli.process_github --output data/processed/github_chunks.jsonl
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

from backend.services.ingestion.github_ingestion import load_github_documents
from backend.services.chunking.github_chunker import GitHubChunker

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_chunks_to_jsonl(chunks: List[Dict[str, Any]], output_path: Path) -> None:
    """Save chunks to JSONL format."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with output_path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    
    logger.info(f"💾 Saved {len(chunks)} chunks to {output_path}")


def process_github_repositories(
    output_path: Path,
    target_words: int = 150,
    max_words: int = 200
) -> None:
    """
    Complete GitHub processing pipeline: ingest -> chunk -> save.
    
    Args:
        output_path: Path to save JSONL chunks
        target_words: Target words per chunk
        max_words: Maximum words per chunk
    """
    
    logger.info("🚀 Starting GitHub repository processing...")
    
    # Step 1: Ingest GitHub documents
    logger.info("📥 Ingesting GitHub repositories...")
    try:
        documents = load_github_documents()
        if not documents:
            logger.warning("⚠️ No GitHub documents found. Check your GITHUB_USERNAME and GITHUB_API_TOKEN.")
            return
        
        logger.info(f"✅ Ingested {len(documents)} GitHub documents")
        
        # Show some stats
        repo_count = len(set(doc.get("repo_name") for doc in documents))
        readme_count = sum(1 for doc in documents if doc.get("type") == "readme")
        repo_summary_count = sum(1 for doc in documents if doc.get("type") == "repository")
        
        logger.info(f"📊 Documents: {repo_count} repos, {repo_summary_count} summaries, {readme_count} READMEs")
        
    except Exception as e:
        logger.error(f"❌ Failed to ingest GitHub documents: {e}")
        raise
    
    # Step 2: Chunk the documents
    logger.info("✂️ Chunking GitHub documents...")
    try:
        chunker = GitHubChunker(target_words=target_words, max_words=max_words)
        chunks = chunker.chunk_github_documents(documents)
        
        if not chunks:
            logger.warning("⚠️ No chunks generated from GitHub documents")
            return
        
        logger.info(f"✅ Generated {len(chunks)} chunks")
        
        # Show chunking stats
        stats = chunker.get_chunk_stats(chunks)
        logger.info(f"📊 Chunk stats: {stats}")
        
    except Exception as e:
        logger.error(f"❌ Failed to chunk GitHub documents: {e}")
        raise
    
    # Step 3: Save to JSONL
    logger.info("💾 Saving chunks to JSONL...")
    try:
        save_chunks_to_jsonl(chunks, output_path)
        logger.info(f"✅ Saved chunks to {output_path}")
        
    except Exception as e:
        logger.error(f"❌ Failed to save chunks: {e}")
        raise
    
    # Final summary
    logger.info("\n🎉 GitHub processing complete!")
    logger.info(f"📁 Output: {output_path}")
    logger.info(f"📊 Total chunks: {len(chunks)}")
    logger.info(f"📊 Repositories processed: {stats.get('repositories', 0)}")
    
    # Show next steps
    logger.info("\n📋 Next steps:")
    logger.info(f"   1. Review chunks: head {output_path}")
    logger.info(f"   2. Embed and upsert: python -m backend.cli.embed_and_upsert --input {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Process GitHub repositories into chunks")
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output JSONL file path (e.g., data/processed/github_chunks.jsonl)"
    )
    parser.add_argument(
        "--target-words",
        type=int,
        default=150,
        help="Target words per chunk (default: 150)"
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=200,
        help="Maximum words per chunk (default: 200)"
    )
    
    args = parser.parse_args()
    
    try:
        process_github_repositories(
            output_path=args.output,
            target_words=args.target_words,
            max_words=args.max_words
        )
    except Exception as e:
        logger.error(f"❌ GitHub processing failed: {e}")
        exit(1)


if __name__ == "__main__":
    main() 