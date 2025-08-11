"""
Medium Blog Ingester
Fetches and processes Medium blog posts from RSS feeds for RAG indexing.
"""

import feedparser
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
from pathlib import Path
import html
from urllib.parse import urljoin, urlparse
import time
import logging
import os
import certifi

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MediumIngester:
    """Ingests Medium blog posts from RSS feeds."""
    
    def __init__(self, max_posts: int = 50, include_drafts: bool = False):
        """
        Initialize the Medium ingester.
        
        Args:
            max_posts: Maximum number of posts to fetch (default: 50)
            include_drafts: Whether to include draft posts (default: False)
        """
        self.max_posts = max_posts
        self.include_drafts = include_drafts
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AI-Charlotte-RAG-Bot/1.0 (Educational/Portfolio Project)'
        })
    
    def fetch_posts(self, rss_url: str) -> List[Dict[str, Any]]:
        """
        Fetch blog posts from Medium RSS feed.
        
        Args:
            rss_url: URL of the Medium RSS feed (e.g., https://medium.com/feed/@username)
            
        Returns:
            List of processed blog post dictionaries
        """
        logger.info(f"Fetching Medium posts from: {rss_url}")
        
        try:
            # Fetch RSS content with proper SSL verification for production
            # Use environment variable to allow SSL bypass in development if needed
            verify_ssl = os.getenv('VERIFY_SSL', 'true').lower() == 'true'
            ssl_verify = certifi.where() if verify_ssl else False
            
            response = self.session.get(rss_url, verify=ssl_verify, timeout=30)
            response.raise_for_status()
            
            # Parse RSS feed from the content
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                logger.warning(f"RSS feed may have issues: {feed.bozo_exception}")
                # Don't return empty if it's just an SSL warning - check if we got entries
            
            if not feed.entries:
                logger.warning("No entries found in RSS feed")
                # Try to get more info about what went wrong
                if hasattr(feed, 'status'):
                    logger.warning(f"Feed status: {feed.status}")
                if hasattr(feed, 'href'):
                    logger.warning(f"Feed href: {feed.href}")
                return []
            
            # Extract author info
            author_info = self._extract_author_info(feed)
            logger.info(f"Found {len(feed.entries)} posts by {author_info.get('name', 'Unknown')}")
            
            # Process entries
            posts = []
            for i, entry in enumerate(feed.entries[:self.max_posts]):
                try:
                    post = self._process_entry(entry, author_info)
                    if post and (self.include_drafts or not post.get('is_draft', False)):
                        posts.append(post)
                        logger.info(f"Processed post {i+1}: {post['title'][:50]}...")
                    
                    # Be respectful with requests
                    if i > 0 and i % 10 == 0:
                        time.sleep(1)
                        
                except Exception as e:
                    logger.error(f"Error processing entry {i}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(posts)} posts")
            return posts
            
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL certificate error when fetching RSS feed: {e}")
            logger.info("Consider checking your system's SSL certificates or network configuration")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching RSS feed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching RSS feed: {e}")
            raise
    
    def _extract_author_info(self, feed) -> Dict[str, Any]:
        """Extract author information from the RSS feed."""
        author_info = {
            'name': 'Unknown Author',
            'url': '',
            'description': ''
        }
        
        # Try to get author info from feed metadata
        if hasattr(feed.feed, 'title'):
            # Medium RSS titles are usually "Stories by [Author] on Medium"
            title = feed.feed.title
            if 'Stories by' in title and 'on Medium' in title:
                author_name = title.replace('Stories by ', '').replace(' on Medium', '').strip()
                author_info['name'] = author_name
        
        if hasattr(feed.feed, 'link'):
            author_info['url'] = feed.feed.link
        
        if hasattr(feed.feed, 'description'):
            author_info['description'] = feed.feed.description
        
        return author_info
    
    def _process_entry(self, entry, author_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single RSS entry into a structured post."""
        try:
            # Extract basic metadata
            title = entry.title if hasattr(entry, 'title') else 'Untitled'
            url = entry.link if hasattr(entry, 'link') else ''
            
            # Parse publication date
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, 'published'):
                try:
                    published_date = datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z')
                except:
                    pass
            
            # Extract and clean content
            content = self._extract_content(entry)
            if not content or len(content.strip()) < 100:
                logger.warning(f"Skipping post with insufficient content: {title}")
                return None
            
            # Extract tags/categories
            tags = self._extract_tags(entry)
            
            # Calculate reading time (rough estimate: 200 words per minute)
            word_count = len(content.split())
            reading_time = max(1, round(word_count / 200))
            
            # Check if it's a draft (usually indicated by specific patterns)
            is_draft = self._is_draft_post(entry, content)
            
            return {
                'title': title,
                'url': url,
                'content': content,
                'author': author_info['name'],
                'author_url': author_info['url'],
                'published_date': published_date,
                'tags': tags,
                'word_count': word_count,
                'reading_time': reading_time,
                'is_draft': is_draft,
                'source': 'medium',
                'raw_entry': {
                    'id': getattr(entry, 'id', ''),
                    'guid': getattr(entry, 'guid', ''),
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing entry: {e}")
            return None
    
    def _extract_content(self, entry) -> str:
        """Extract and clean the main content from an RSS entry."""
        content = ""
        
        # Try different content fields
        if hasattr(entry, 'content') and entry.content:
            content = entry.content[0].value if entry.content else ""
        elif hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        
        if not content:
            return ""
        
        # Clean HTML content
        content = self._clean_html_content(content)
        
        # Remove Medium-specific artifacts
        content = self._remove_medium_artifacts(content)
        
        return content.strip()
    
    def _clean_html_content(self, html_content: str) -> str:
        """Clean HTML content and convert to plain text."""
        # Decode HTML entities
        content = html.unescape(html_content)
        
        # Remove HTML tags but preserve structure
        content = re.sub(r'<br\s*/?>', '\n', content)  # Convert <br> to newlines
        content = re.sub(r'</p>', '\n\n', content)     # Convert </p> to double newlines
        content = re.sub(r'<h[1-6][^>]*>', '\n\n## ', content)  # Convert headers
        content = re.sub(r'</h[1-6]>', '\n\n', content)
        content = re.sub(r'<li[^>]*>', '\n- ', content)  # Convert list items
        content = re.sub(r'<blockquote[^>]*>', '\n> ', content)  # Convert blockquotes
        
        # Remove all remaining HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Clean up whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Multiple newlines to double
        content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces to single
        
        return content.strip()
    
    def _remove_medium_artifacts(self, content: str) -> str:
        """Remove Medium-specific artifacts and noise."""
        # Remove common Medium footers/headers
        patterns_to_remove = [
            r'Originally published at.*',
            r'Follow.*on Medium.*',
            r'Sign up for.*',
            r'Get the Medium app.*',
            r'\d+ min read',
            r'Photo by.*on Unsplash',
            r'Image source:.*',
            r'Continue reading on Medium.*',
        ]
        
        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Remove URLs that are likely tracking or Medium-specific
        content = re.sub(r'https://cdn-images-\d+\.medium\.com/[^\s]+', '', content)
        content = re.sub(r'https://medium\.com/[^\s]*\?source=[^\s]+', '', content)
        
        return content.strip()
    
    def _extract_tags(self, entry) -> List[str]:
        """Extract tags/categories from the entry."""
        tags = []
        
        # Try different tag fields
        if hasattr(entry, 'tags') and entry.tags:
            tags.extend([tag.term for tag in entry.tags if hasattr(tag, 'term')])
        
        if hasattr(entry, 'categories') and entry.categories:
            for cat in entry.categories:
                if isinstance(cat, str):
                    tags.append(cat)
                elif hasattr(cat, 'term'):
                    tags.append(cat.term)
        
        # Clean and deduplicate tags
        cleaned_tags = []
        for tag in tags:
            if tag and isinstance(tag, str):
                clean_tag = tag.strip().lower()
                if clean_tag and clean_tag not in cleaned_tags:
                    cleaned_tags.append(clean_tag)
        
        return cleaned_tags
    
    def _is_draft_post(self, entry, content: str) -> bool:
        """Determine if a post is a draft (usually not fully published)."""
        # Check for draft indicators in title or content
        draft_indicators = [
            'draft', '[draft]', '(draft)', 'work in progress', 'wip',
            'coming soon', 'preview', 'snippet'
        ]
        
        title = getattr(entry, 'title', '').lower()
        content_lower = content[:200].lower()  # Check first 200 chars
        
        for indicator in draft_indicators:
            if indicator in title or indicator in content_lower:
                return True
        
        # Very short content might be a draft
        if len(content.strip()) < 200:
            return True
        
        return False
    
    def save_posts_to_jsonl(self, posts: List[Dict[str, Any]], output_path: Path) -> None:
        """Save processed posts to JSONL format."""
        import json
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for post in posts:
                # Create a clean version for JSONL (remove datetime objects)
                clean_post = post.copy()
                if clean_post.get('published_date'):
                    clean_post['published_date'] = clean_post['published_date'].isoformat()
                
                f.write(json.dumps(clean_post, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(posts)} posts to {output_path}")
    
    def get_post_stats(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics about the fetched posts."""
        if not posts:
            return {'total_posts': 0}
        
        total_words = sum(post['word_count'] for post in posts)
        total_reading_time = sum(post['reading_time'] for post in posts)
        
        # Get all unique tags
        all_tags = set()
        for post in posts:
            all_tags.update(post.get('tags', []))
        
        # Get date range
        dates = [post['published_date'] for post in posts if post.get('published_date')]
        date_range = {}
        if dates:
            date_range = {
                'earliest': min(dates),
                'latest': max(dates)
            }
        
        return {
            'total_posts': len(posts),
            'total_words': total_words,
            'avg_words_per_post': total_words // len(posts) if posts else 0,
            'total_reading_time': total_reading_time,
            'unique_tags': len(all_tags),
            'popular_tags': list(all_tags)[:10],  # First 10 tags
            'date_range': date_range,
            'drafts_count': len([p for p in posts if p.get('is_draft', False)])
        }


def validate_medium_rss_url(url: str) -> bool:
    """Validate that a URL is a proper Medium RSS feed."""
    if not url:
        return False
    
    # Check URL format
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return False
    
    # Should contain medium.com and /feed/
    if 'medium.com' not in parsed.netloc.lower():
        return False
    
    if '/feed/' not in parsed.path:
        return False
    
    return True


def get_medium_rss_url(username: str) -> str:
    """Generate Medium RSS URL from username."""
    if username.startswith('@'):
        username = username[1:]  # Remove @ if present
    
    return f"https://medium.com/feed/@{username}"


if __name__ == "__main__":
    # Example usage
    ingester = MediumIngester(max_posts=10)
    
    # Test with Charlotte's feed
    rss_url = "https://medium.com/feed/@charlotteqazi"
    
    try:
        posts = ingester.fetch_posts(rss_url)
        stats = ingester.get_post_stats(posts)
        
        print(f"Fetched {stats['total_posts']} posts")
        print(f"Total words: {stats['total_words']:,}")
        print(f"Average words per post: {stats['avg_words_per_post']:,}")
        print(f"Popular tags: {stats['popular_tags']}")
        
        if posts:
            print(f"\nFirst post: {posts[0]['title']}")
            print(f"Content preview: {posts[0]['content'][:200]}...")
        
    except Exception as e:
        print(f"Error: {e}") 