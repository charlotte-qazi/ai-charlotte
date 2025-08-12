#!/usr/bin/env python3
"""
AI Charlotte - Embedding and Vector Database CLI
Copyright (c) 2025 Charlotte Qazi

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Any

from backend.core.config import settings
from backend.services.embedding.embeddings import EmbeddingClient
from backend.services.vector_store.qdrant_client import QdrantVectorStore


def load_jsonl_chunks(jsonl_path: Path) -> List[Dict[str, Any]]:
    """Load chunks from JSONL file."""
    chunks = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                chunk = json.loads(line.strip())
                chunks.append(chunk)
            except json.JSONDecodeError as e:
                print(f"⚠️  Error parsing line {line_num}: {e}")
    return chunks


def embed_and_upsert(
    jsonl_path: Path,
    collection_name: str,
    batch_size: int = 50,
    recreate_collection: bool = False
) -> None:
    """Embed JSONL chunks and upsert to Qdrant."""
    
    # Validate environment
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required in .env file")
    if not settings.qdrant_url:
        raise ValueError("QDRANT_URL is required in .env file")
    
    print(f"🔍 Loading chunks from: {jsonl_path}")
    
    # Load chunks
    chunks = load_jsonl_chunks(jsonl_path)
    if not chunks:
        print("❌ No chunks found in JSONL file")
        return
    
    print(f"📦 Loaded {len(chunks)} chunks")
    
    # Initialize clients
    print("🤖 Initializing OpenAI embeddings client...")
    embedding_client = EmbeddingClient(
        api_key=settings.openai_api_key,
        model="text-embedding-3-small"
    )
    
    print("🗄️ Initializing Qdrant client...")
    vector_store = QdrantVectorStore(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        collection=collection_name
    )
    
    # Create or recreate collection
    vector_size = embedding_client.get_embedding_dimension()
    if recreate_collection:
        try:
            vector_store.delete_collection()
        except Exception:
            pass  # Collection might not exist
    
    vector_store.create_collection(vector_size=vector_size)
    
    # Extract text for embedding
    texts = [chunk["text"] for chunk in chunks]
    chunk_ids = [chunk["id"] for chunk in chunks]
    
    print(f"🧮 Generating embeddings for {len(texts)} chunks...")
    
    # Generate embeddings in batches
    embeddings = embedding_client.embed_texts(texts, batch_size=batch_size)
    
    print(f"✅ Generated {len(embeddings)} embeddings")
    
    # Prepare payloads (metadata for each chunk)
    payloads = []
    for chunk in chunks:
        payload = {
            "text": chunk["text"],
            "source": chunk["source"],
            "chunk_index": chunk["chunk_index"],
            "metadata": chunk.get("metadata", {})
        }
        payloads.append(payload)
    
    # Upsert to Qdrant
    print(f"📤 Upserting to Qdrant collection '{collection_name}'...")
    vector_store.upsert(
        vectors=embeddings,
        payloads=payloads,
        ids=chunk_ids
    )
    
    # Verify upload
    count = vector_store.count()
    print(f"✅ Collection now contains {count} points")
    
    # Show collection info
    info = vector_store.get_collection_info()
    print(f"📊 Collection info: {info}")
    
    print(f"\n🎉 Successfully embedded and upserted {len(chunks)} chunks!")


def main():
    parser = argparse.ArgumentParser(description="Embed JSONL chunks and upsert to Qdrant")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to input JSONL file (e.g., data/processed/cv_chunks.jsonl)"
    )
    parser.add_argument(
        "--collection",
        type=str,
        default=None,
        help="Qdrant collection name (default: from settings)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for embedding generation (default: 50)"
    )
    parser.add_argument(
        "--recreate-collection",
        action="store_true",
        help="Recreate the collection (deletes existing data)"
    )
    
    args = parser.parse_args()
    
    collection_name = args.collection or settings.qdrant_collection
    
    try:
        embed_and_upsert(
            jsonl_path=args.input,
            collection_name=collection_name,
            batch_size=args.batch_size,
            recreate_collection=args.recreate_collection
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)


if __name__ == "__main__":
    main() 