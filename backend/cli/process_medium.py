#!/usr/bin/env python3
"""
AI Charlotte - Medium Blog Processing CLI
Copyright (c) 2025 Charlotte Qazi

Fetches Medium blog posts from RSS and processes them into chunks for RAG indexing.

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

import argparse
import sys
from pathlib import Path
import json
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.ingestion.medium_ingester import MediumIngester, validate_medium_rss_url, get_medium_rss_url
from backend.services.chunking.blog_chunker import BlogChunker


def process_medium_blog(rss_url: str, output_path: str = None, max_posts: int = 50, 
                       target_words: int = 200, max_words: int = 400) -> Dict[str, Any]:
    """
    Process Medium blog posts from RSS feed.
    
    Args:
        rss_url: Medium RSS feed URL
        output_path: Output JSONL file path (optional)
        max_posts: Maximum number of posts to process
        target_words: Target words per chunk
        max_words: Maximum words per chunk
        
    Returns:
        Processing statistics
    """
    print(f"🔍 Processing Medium blog from: {rss_url}")
    
    # Initialize ingester and chunker
    ingester = MediumIngester(max_posts=max_posts)
    chunker = BlogChunker(target_words=target_words, max_words=max_words)
    
    try:
        # Fetch blog posts
        print("📡 Fetching blog posts...")
        posts = ingester.fetch_posts(rss_url)
        
        if not posts:
            print("❌ No posts found or processed")
            return {'error': 'No posts found'}
        
        post_stats = ingester.get_post_stats(posts)
        print(f"✅ Fetched {post_stats['total_posts']} posts")
        print(f"   Total words: {post_stats['total_words']:,}")
        print(f"   Date range: {post_stats.get('date_range', {}).get('earliest', 'Unknown')} to {post_stats.get('date_range', {}).get('latest', 'Unknown')}")
        
        # Process posts into chunks
        print("\n🔧 Chunking blog posts...")
        all_chunks = []
        
        for i, post in enumerate(posts):
            try:
                chunks = chunker.chunk_blog_post(post)
                all_chunks.extend(chunks)
                print(f"   Post {i+1}: '{post['title'][:50]}...' → {len(chunks)} chunks")
            except Exception as e:
                print(f"   ❌ Error chunking post {i+1}: {e}")
                continue
        
        if not all_chunks:
            print("❌ No chunks generated")
            return {'error': 'No chunks generated'}
        
        chunking_stats = chunker.get_chunking_stats(all_chunks)
        print(f"\n✅ Generated {chunking_stats['total_chunks']} chunks")
        print(f"   Average words per chunk: {chunking_stats['avg_words_per_chunk']}")
        print(f"   Chunk types: {chunking_stats['chunk_types']}")
        
        # Determine output path
        if not output_path:
            # Extract author name for filename
            author_name = posts[0].get('author', 'unknown').lower().replace(' ', '-')
            output_path = f"data/processed/{author_name}_medium_chunks.jsonl"
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save chunks to JSONL
        print(f"\n💾 Saving chunks to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            for chunk in all_chunks:
                f.write(json.dumps(chunk, ensure_ascii=False, default=str) + '\n')
        
        print(f"✅ Saved {len(all_chunks)} chunks to {output_file}")
        
        # Return comprehensive stats
        return {
            'success': True,
            'output_file': str(output_file),
            'posts_processed': len(posts),
            'chunks_generated': len(all_chunks),
            'post_stats': post_stats,
            'chunking_stats': chunking_stats,
            'sample_chunks': [
                {
                    'title': chunk['source'],
                    'heading': chunk['heading'],
                    'type': chunk['chunk_type'],
                    'words': chunk['word_count']
                }
                for chunk in all_chunks[:3]  # First 3 chunks as samples
            ]
        }
        
    except Exception as e:
        print(f"❌ Error processing Medium blog: {e}")
        return {'error': str(e)}


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Process Medium blog posts from RSS feed into RAG-ready chunks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process Charlotte's Medium blog
  python -m backend.cli.process_medium https://medium.com/feed/@charlotteqazi
  
  # Process with custom settings
  python -m backend.cli.process_medium https://medium.com/feed/@username \\
    --output data/processed/my_blog.jsonl \\
    --max-posts 20 \\
    --max-words 300
  
  # Process using just username
  python -m backend.cli.process_medium @username
        """
    )
    
    parser.add_argument(
        'rss_url',
        help='Medium RSS feed URL (e.g., https://medium.com/feed/@username) or just @username'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output JSONL file path (default: data/processed/{author}_medium_chunks.jsonl)'
    )
    
    parser.add_argument(
        '--max-posts',
        type=int,
        default=50,
        help='Maximum number of posts to process (default: 50)'
    )
    
    parser.add_argument(
        '--target-words',
        type=int,
        default=200,
        help='Target words per chunk (default: 200)'
    )
    
    parser.add_argument(
        '--max-words',
        type=int,
        default=400,
        help='Maximum words per chunk (default: 400)'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate the RSS URL without processing'
    )
    
    args = parser.parse_args()
    
    # Handle username format (convert @username to full RSS URL)
    rss_url = args.rss_url
    if rss_url.startswith('@'):
        rss_url = get_medium_rss_url(rss_url)
        print(f"🔗 Converted username to RSS URL: {rss_url}")
    
    # Validate RSS URL
    if not validate_medium_rss_url(rss_url):
        print(f"❌ Invalid Medium RSS URL: {rss_url}")
        print("Expected format: https://medium.com/feed/@username")
        print("Or just provide: @username")
        sys.exit(1)
    
    if args.validate_only:
        print(f"✅ Valid Medium RSS URL: {rss_url}")
        sys.exit(0)
    
    # Process the blog
    result = process_medium_blog(
        rss_url=rss_url,
        output_path=args.output,
        max_posts=args.max_posts,
        target_words=args.target_words,
        max_words=args.max_words
    )
    
    if result.get('error'):
        print(f"❌ Processing failed: {result['error']}")
        sys.exit(1)
    
    # Print final summary
    print("\n" + "="*60)
    print("📊 PROCESSING SUMMARY")
    print("="*60)
    print(f"✅ Successfully processed Medium blog")
    print(f"📝 Posts processed: {result['posts_processed']}")
    print(f"🧩 Chunks generated: {result['chunks_generated']}")
    print(f"💾 Output file: {result['output_file']}")
    
    if result.get('sample_chunks'):
        print(f"\n📋 Sample chunks:")
        for i, sample in enumerate(result['sample_chunks'], 1):
            print(f"   {i}. {sample['title'][:40]}... → {sample['heading']} ({sample['words']} words)")
    
    print(f"\n🚀 Ready for embedding! Use:")
    print(f"   python -m backend.cli.embed_and_upsert --input {result['output_file']} --collection ai_charlotte")


if __name__ == "__main__":
    main() 