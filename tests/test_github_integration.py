"""
Tests for GitHub repository integration.
Tests ingestion, chunking, and end-to-end pipeline.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from pathlib import Path
from typing import List, Dict, Any

from backend.services.ingestion.github_ingestion import (
    fetch_repos, 
    fetch_repo_languages,
    fetch_repo_topics,
    fetch_readme,
    fetch_repo_details,
    load_github_documents,
    create_repo_summary_text
)
from backend.services.chunking.github_chunker import GitHubChunker


class TestGitHubIngestion:
    """Test GitHub API ingestion functionality."""
    
    @patch('backend.services.ingestion.github_ingestion.make_github_request')
    def test_fetch_repos_single_page(self, mock_request):
        """Test fetching repositories with single page."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "repo1", "full_name": "user/repo1"},
            {"name": "repo2", "full_name": "user/repo2"}
        ]
        mock_request.return_value = mock_response
        
        repos = fetch_repos("testuser")
        
        assert len(repos) == 2
        assert repos[0]["name"] == "repo1"
        assert repos[1]["name"] == "repo2"
    
    @patch('backend.services.ingestion.github_ingestion.make_github_request')
    def test_fetch_repos_pagination(self, mock_request):
        """Test fetching repositories with pagination."""
        # First page
        mock_response1 = Mock()
        mock_response1.status_code = 200
        mock_response1.json.return_value = [{"name": f"repo{i}"} for i in range(100)]
        
        # Second page (partial)
        mock_response2 = Mock()
        mock_response2.status_code = 200
        mock_response2.json.return_value = [{"name": f"repo{i}"} for i in range(100, 120)]
        
        # Third page (empty)
        mock_response3 = Mock()
        mock_response3.status_code = 200
        mock_response3.json.return_value = []
        
        mock_request.side_effect = [mock_response1, mock_response2, mock_response3]
        
        repos = fetch_repos("testuser")
        
        assert len(repos) == 120
        assert repos[0]["name"] == "repo0"
        assert repos[119]["name"] == "repo119"
    
    @patch('backend.services.ingestion.github_ingestion.make_github_request')
    def test_fetch_repo_languages(self, mock_request):
        """Test fetching repository languages."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Python": 15000,
            "JavaScript": 8000,
            "CSS": 2000
        }
        mock_request.return_value = mock_response
        
        languages = fetch_repo_languages("user", "repo")
        
        assert languages["Python"] == 15000
        assert languages["JavaScript"] == 8000
        assert languages["CSS"] == 2000
    
    @patch('backend.services.ingestion.github_ingestion.make_github_request')
    def test_fetch_repo_topics(self, mock_request):
        """Test fetching repository topics."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "names": ["python", "web-development", "api"]
        }
        mock_request.return_value = mock_response
        
        topics = fetch_repo_topics("user", "repo")
        
        assert topics == ["python", "web-development", "api"]
    
    @patch('backend.services.ingestion.github_ingestion.make_github_request')
    def test_fetch_readme_base64(self, mock_request):
        """Test fetching README with base64 encoding."""
        import base64
        
        readme_content = "# Test Repository\n\nThis is a test README."
        encoded_content = base64.b64encode(readme_content.encode('utf-8')).decode('utf-8')
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "encoding": "base64",
            "content": encoded_content
        }
        mock_request.return_value = mock_response
        
        readme = fetch_readme("user", "repo")
        
        assert readme == readme_content
    
    @patch('backend.services.ingestion.github_ingestion.make_github_request')
    def test_fetch_readme_no_readme(self, mock_request):
        """Test fetching README when none exists."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response
        
        readme = fetch_readme("user", "repo")
        
        assert readme == ""
    
    def test_create_repo_summary_text(self):
        """Test creating repository summary text."""
        repo_details = {
            "name": "test-repo",
            "description": "A test repository",
            "primary_language": "Python",
            "language_percentages": {"Python": 80.0, "JavaScript": 20.0},
            "topics": ["python", "testing"],
            "stars": 42,
            "forks": 7,
            "homepage": "https://example.com",
            "license": "MIT",
            "is_private": False,
            "is_fork": False,
            "is_archived": False,
            "url": "https://github.com/user/test-repo"
        }
        
        summary = create_repo_summary_text(repo_details)
        
        assert "Repository: test-repo" in summary
        assert "Description: A test repository" in summary
        assert "Primary Language: Python" in summary
        assert "Languages: Python (80.0%), JavaScript (20.0%)" in summary
        assert "Topics: python, testing" in summary
        assert "Stats: 42 stars, 7 forks" in summary
        assert "Homepage: https://example.com" in summary
        assert "License: MIT" in summary
        assert "Repository URL: https://github.com/user/test-repo" in summary
    
    @patch('backend.services.ingestion.github_ingestion.fetch_repo_details')
    @patch('backend.services.ingestion.github_ingestion.fetch_repos')
    def test_load_github_documents(self, mock_fetch_repos, mock_fetch_details):
        """Test loading GitHub documents end-to-end."""
        # Mock repository data
        mock_fetch_repos.return_value = [
            {"name": "repo1", "full_name": "user/repo1"},
            {"name": "repo2", "full_name": "user/repo2"}
        ]
        
        # Mock detailed repo data
        mock_fetch_details.side_effect = [
            {
                "name": "repo1",
                "full_name": "user/repo1",
                "description": "First repo",
                "url": "https://github.com/user/repo1",
                "clone_url": "https://github.com/user/repo1.git",
                "ssh_url": "git@github.com:user/repo1.git",
                "homepage": "",
                "primary_language": "Python",
                "languages": {"Python": 1000},
                "language_percentages": {"Python": 100.0},
                "topics": ["python"],
                "readme": "# Repo 1\nThis is repo 1",
                "stars": 5,
                "forks": 1,
                "watchers": 5,
                "size": 100,
                "is_private": False,
                "is_fork": False,
                "is_archived": False,
                "default_branch": "main",
                "open_issues": 0,
                "license": "MIT",
                "created_at": "2023-01-01",
                "updated_at": "2023-12-01",
                "pushed_at": "2023-12-01"
            },
            {
                "name": "repo2", 
                "full_name": "user/repo2",
                "description": "Second repo",
                "url": "https://github.com/user/repo2",
                "clone_url": "https://github.com/user/repo2.git",
                "ssh_url": "git@github.com:user/repo2.git",
                "homepage": "",
                "primary_language": "JavaScript",
                "languages": {"JavaScript": 2000},
                "language_percentages": {"JavaScript": 100.0},
                "topics": ["javascript", "web"],
                "readme": "",  # No README
                "stars": 0,
                "forks": 0,
                "watchers": 0,
                "size": 50,
                "is_private": False,
                "is_fork": False,
                "is_archived": False,
                "default_branch": "main",
                "open_issues": 2,
                "license": None,
                "created_at": "2023-06-01",
                "updated_at": "2023-11-01",
                "pushed_at": "2023-11-01"
            }
        ]
        
        with patch.dict('os.environ', {'GITHUB_USERNAME': 'testuser', 'GITHUB_API_TOKEN': 'token'}):
            documents = load_github_documents()
        
        # Should have 3 documents: 2 repo summaries + 1 README
        assert len(documents) == 3
        
        # Check repository documents
        repo_docs = [doc for doc in documents if doc["type"] == "repository"]
        assert len(repo_docs) == 2
        
        # Check README documents
        readme_docs = [doc for doc in documents if doc["type"] == "readme"]
        assert len(readme_docs) == 1
        assert readme_docs[0]["repo_name"] == "repo1"


class TestGitHubChunker:
    """Test GitHub document chunking functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.chunker = GitHubChunker(target_words=50, max_words=100)
    
    def test_chunk_repository_summary_small(self):
        """Test chunking a small repository summary."""
        document = {
            "text": "Repository: test-repo\nDescription: A small test repository\nLanguage: Python",
            "type": "repository",
            "repo_name": "test-repo",
            "repo_url": "https://github.com/user/test-repo",
            "metadata": {"primary_language": "Python"}
        }
        
        chunks = self.chunker._chunk_single_document(document)
        
        assert len(chunks) == 1
        assert chunks[0]["id"] == "github_repo_test-repo_summary"
        assert chunks[0]["metadata"]["type"] == "repository_summary"
        assert chunks[0]["metadata"]["repo_name"] == "test-repo"
    
    def test_chunk_readme_with_sections(self):
        """Test chunking README with clear sections."""
        readme_text = """# Test Repository

This is the introduction to the test repository.

## Installation

To install this project, run the following commands:
```bash
npm install
```

## Usage

Here's how to use this project:
1. Import the module
2. Call the main function
3. Handle the results

## Contributing

We welcome contributions! Please follow these guidelines:
- Fork the repository
- Create a feature branch
- Submit a pull request
"""
        
        document = {
            "text": readme_text,
            "type": "readme",
            "repo_name": "test-repo",
            "repo_url": "https://github.com/user/test-repo",
            "metadata": {"primary_language": "JavaScript"}
        }
        
        chunks = self.chunker._chunk_single_document(document)
        
        assert len(chunks) >= 1  # Should have at least one section
        
        # Check that chunks have proper IDs and metadata
        for i, chunk in enumerate(chunks):
            assert chunk["id"].startswith("github_readme_test-repo_section_")
            assert chunk["metadata"]["type"] == "readme_section"
            assert chunk["metadata"]["repo_name"] == "test-repo"
            assert "word_count" in chunk["metadata"]
    
    def test_chunk_long_readme_section(self):
        """Test chunking a very long README section."""
        # Create a long section that will need to be split
        long_text = " ".join([f"This is sentence number {i} in a very long README section." for i in range(1, 101)])
        
        document = {
            "text": f"# Long Section\n\n{long_text}",
            "type": "readme",
            "repo_name": "long-repo",
            "repo_url": "https://github.com/user/long-repo",
            "metadata": {}
        }
        
        chunks = self.chunker._chunk_single_document(document)
        
        # Should split into multiple chunks due to length
        assert len(chunks) > 1
        
        # Each chunk should be under max_words
        for chunk in chunks:
            word_count = len(chunk["text"].split())
            assert word_count <= self.chunker.max_words
    
    def test_chunk_github_documents_mixed(self):
        """Test chunking mixed GitHub documents."""
        documents = [
            {
                "text": "Repository: repo1\nDescription: First repository\nLanguage: Python",
                "type": "repository",
                "repo_name": "repo1",
                "repo_url": "https://github.com/user/repo1",
                "metadata": {"primary_language": "Python"}
            },
            {
                "text": "# Repo 1\n\nThis is the README for repo1.\n\n## Features\n\n- Feature 1\n- Feature 2",
                "type": "readme",
                "repo_name": "repo1", 
                "repo_url": "https://github.com/user/repo1",
                "metadata": {"primary_language": "Python"}
            },
            {
                "text": "Repository: repo2\nDescription: Second repository\nLanguage: JavaScript",
                "type": "repository",
                "repo_name": "repo2",
                "repo_url": "https://github.com/user/repo2", 
                "metadata": {"primary_language": "JavaScript"}
            }
        ]
        
        chunks = self.chunker.chunk_github_documents(documents)
        
        assert len(chunks) >= 3  # At least one chunk per document
        
        # Check we have both types
        repo_chunks = [c for c in chunks if c["metadata"]["type"] == "repository_summary"]
        readme_chunks = [c for c in chunks if c["metadata"]["type"] == "readme_section"]
        
        assert len(repo_chunks) == 2
        assert len(readme_chunks) >= 1
    
    def test_get_chunk_stats(self):
        """Test getting statistics from chunks."""
        chunks = [
            {
                "metadata": {
                    "type": "repository_summary",
                    "repo_name": "repo1",
                    "word_count": 25
                }
            },
            {
                "metadata": {
                    "type": "readme_section", 
                    "repo_name": "repo1",
                    "word_count": 75
                }
            },
            {
                "metadata": {
                    "type": "repository_summary",
                    "repo_name": "repo2",
                    "word_count": 30
                }
            }
        ]
        
        stats = self.chunker.get_chunk_stats(chunks)
        
        assert stats["total_chunks"] == 3
        assert stats["avg_words_per_chunk"] == (25 + 75 + 30) / 3
        assert stats["min_words"] == 25
        assert stats["max_words"] == 75
        assert stats["chunk_types"]["repository_summary"] == 2
        assert stats["chunk_types"]["readme_section"] == 1
        assert stats["repositories"] == 2


class TestGitHubEndToEnd:
    """Test end-to-end GitHub integration pipeline."""
    
    @patch('backend.services.ingestion.github_ingestion.load_github_documents')
    def test_process_github_pipeline(self, mock_load_docs):
        """Test the complete GitHub processing pipeline."""
        # Mock documents from ingestion
        mock_load_docs.return_value = [
            {
                "text": "Repository: test-repo\nDescription: A test repository\nLanguage: Python",
                "type": "repository",
                "repo_name": "test-repo",
                "repo_url": "https://github.com/user/test-repo",
                "metadata": {"primary_language": "Python", "topics": ["python", "testing"]}
            },
            {
                "text": "# Test Repo\n\nThis is a test repository for demonstration purposes.\n\n## Features\n\n- Feature A\n- Feature B",
                "type": "readme",
                "repo_name": "test-repo",
                "repo_url": "https://github.com/user/test-repo",
                "metadata": {"primary_language": "Python", "topics": ["python", "testing"]}
            }
        ]
        
        # Process through chunker
        chunker = GitHubChunker(target_words=50, max_words=100)
        chunks = chunker.chunk_github_documents(mock_load_docs.return_value)
        
        # Verify results
        assert len(chunks) >= 2  # At least repository + readme chunks
        
        # Check chunk structure matches expected format for embedding
        for chunk in chunks:
            assert "id" in chunk
            assert "text" in chunk
            assert "source" in chunk
            assert chunk["source"] == "github"
            assert "chunk_index" in chunk
            assert "metadata" in chunk
            
            # Check metadata has required fields
            metadata = chunk["metadata"]
            assert "type" in metadata
            assert "repo_name" in metadata
            assert "repo_url" in metadata
            assert "word_count" in metadata
            
            # Verify chunk is properly sized (allow small chunks for tests)
            word_count = len(chunk["text"].split())
            assert word_count >= 5  # More lenient for test data
            assert word_count <= chunker.max_words
    
    def test_chunk_format_for_embedding(self):
        """Test that chunks are in the correct format for embedding pipeline."""
        documents = [
            {
                "text": "Repository: sample-repo\nDescription: Sample repository\nLanguage: TypeScript",
                "type": "repository", 
                "repo_name": "sample-repo",
                "repo_url": "https://github.com/user/sample-repo",
                "metadata": {
                    "primary_language": "TypeScript",
                    "topics": ["typescript", "web"],
                    "stars": 10,
                    "forks": 2
                }
            }
        ]
        
        chunker = GitHubChunker()
        chunks = chunker.chunk_github_documents(documents)
        
        # Verify chunk format matches what embed_and_upsert.py expects
        chunk = chunks[0]
        
        # Required fields for embedding
        assert isinstance(chunk["id"], str)
        assert isinstance(chunk["text"], str)
        assert isinstance(chunk["source"], str)
        assert isinstance(chunk["chunk_index"], int)
        assert isinstance(chunk["metadata"], dict)
        
        # Metadata should be JSON serializable
        import json
        json.dumps(chunk["metadata"])  # Should not raise exception
        
        # Text should be meaningful for embedding
        assert len(chunk["text"]) > 10
        assert "Repository:" in chunk["text"] or "sample-repo" in chunk["text"]


if __name__ == "__main__":
    pytest.main([__file__]) 