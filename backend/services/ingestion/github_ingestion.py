"""
AI Charlotte - GitHub Repository Ingestion Service
Copyright (c) 2025 Charlotte Qazi

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

import os
import requests
import base64
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import logging
import time

load_dotenv()

logger = logging.getLogger(__name__)

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN") 

HEADERS = {
    "Authorization": f"token {GITHUB_API_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Rate limiting
RATE_LIMIT_DELAY = 0.5  # seconds between requests


def make_github_request(url: str, headers: Optional[Dict[str, str]] = None) -> Optional[requests.Response]:
    """Make a GitHub API request with rate limiting and error handling."""
    if headers is None:
        headers = HEADERS
    
    try:
        time.sleep(RATE_LIMIT_DELAY)  # Basic rate limiting
        response = requests.get(url, headers=headers)
        
        if response.status_code == 403 and 'rate limit' in response.text.lower():
            logger.warning("Rate limit hit, waiting 60 seconds...")
            time.sleep(60)
            response = requests.get(url, headers=headers)
        
        return response
    except Exception as e:
        logger.error(f"Request failed for {url}: {e}")
        return None


def fetch_repos(username: str) -> List[dict]:
    """Fetch all repositories for a user, handling pagination."""
    all_repos = []
    page = 1
    per_page = 100  # Max allowed by GitHub API
    
    while True:
        url = f"https://api.github.com/users/{username}/repos"
        params = {
            "page": page,
            "per_page": per_page,
            "sort": "updated",
            "direction": "desc"
        }
        
        response = make_github_request(f"{url}?{'&'.join([f'{k}={v}' for k, v in params.items()])}")
        if not response or response.status_code != 200:
            logger.error(f"Failed to fetch repos page {page}: {response.status_code if response else 'No response'}")
            break
        
        repos = response.json()
        if not repos:  # No more repos
            break
            
        all_repos.extend(repos)
        logger.info(f"Fetched {len(repos)} repos from page {page}")
        
        if len(repos) < per_page:  # Last page
            break
            
        page += 1
    
    logger.info(f"Total repos fetched: {len(all_repos)}")
    return all_repos


def fetch_repo_languages(username: str, repo_name: str) -> Dict[str, int]:
    """Fetch programming languages used in a repository."""
    url = f"https://api.github.com/repos/{username}/{repo_name}/languages"
    response = make_github_request(url)
    
    if response and response.status_code == 200:
        return response.json()
    else:
        logger.warning(f"Failed to fetch languages for {repo_name}")
        return {}


def fetch_repo_topics(username: str, repo_name: str) -> List[str]:
    """Fetch topics/tags for a repository."""
    url = f"https://api.github.com/repos/{username}/{repo_name}/topics"
    headers = {**HEADERS, "Accept": "application/vnd.github.mercy-preview+json"}  # Topics API preview
    
    response = make_github_request(url, headers)
    
    if response and response.status_code == 200:
        data = response.json()
        return data.get("names", [])
    else:
        logger.warning(f"Failed to fetch topics for {repo_name}")
        return []


def fetch_readme(username: str, repo_name: str) -> str:
    """Fetch README content for a repository."""
    url = f"https://api.github.com/repos/{username}/{repo_name}/readme"
    response = make_github_request(url)

    if not response or response.status_code != 200:
        logger.info(f"No README found for {repo_name}")
        return ""

    try:
        readme_data = response.json()
        
        # Handle base64 encoded content
        if readme_data.get("encoding") == "base64":
            content = base64.b64decode(readme_data["content"]).decode('utf-8')
            return content
        
        # Fallback to download URL
        download_url = readme_data.get("download_url")
        if download_url:
            content_response = make_github_request(download_url)
            if content_response and content_response.status_code == 200:
                return content_response.text
                
    except Exception as e:
        logger.error(f"Error processing README for {repo_name}: {e}")
    
    return ""


def fetch_repo_details(username: str, repo: Dict[str, Any]) -> Dict[str, Any]:
    """Fetch comprehensive details for a single repository."""
    repo_name = repo["name"]
    logger.info(f"Processing repository: {repo_name}")
    
    # Get languages
    languages = fetch_repo_languages(username, repo_name)
    
    # Get topics
    topics = fetch_repo_topics(username, repo_name)
    
    # Get README
    readme = fetch_readme(username, repo_name)
    
    # Calculate primary language and language percentages
    total_bytes = sum(languages.values()) if languages else 0
    language_percentages = {}
    if total_bytes > 0:
        language_percentages = {
            lang: round((bytes_count / total_bytes) * 100, 2)
            for lang, bytes_count in languages.items()
        }
    
    primary_language = max(languages, key=lambda x: languages[x]) if languages else None
    
    return {
        "name": repo["name"],
        "full_name": repo["full_name"],
        "description": repo.get("description", ""),
        "url": repo["html_url"],
        "clone_url": repo["clone_url"],
        "ssh_url": repo["ssh_url"],
        "homepage": repo.get("homepage") or "",
        "primary_language": primary_language,
        "languages": languages,
        "language_percentages": language_percentages,
        "topics": topics,
        "readme": readme,
        "stars": repo.get("stargazers_count", 0),
        "forks": repo.get("forks_count", 0),
        "watchers": repo.get("watchers_count", 0),
        "size": repo.get("size", 0),  # in KB
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at"),
        "pushed_at": repo.get("pushed_at"),
        "is_private": repo.get("private", False),
        "is_fork": repo.get("fork", False),
        "is_archived": repo.get("archived", False),
        "default_branch": repo.get("default_branch", "main"),
        "open_issues": repo.get("open_issues_count", 0),
        "license": repo.get("license", {}).get("name") if repo.get("license") else None,
    }


def load_github_documents() -> List[Dict[str, Any]]:
    """Load comprehensive GitHub repository data as documents for RAG."""
    if not GITHUB_USERNAME or not GITHUB_API_TOKEN:
        raise ValueError("GITHUB_USERNAME and GITHUB_API_TOKEN must be set in environment variables")
    
    logger.info(f"Starting GitHub ingestion for user: {GITHUB_USERNAME}")
    
    # Fetch all repositories
    repos = fetch_repos(GITHUB_USERNAME)
    if not repos:
        logger.warning("No repositories found")
        return []
    
    documents = []
    
    for repo in repos:
        try:
            repo_details = fetch_repo_details(GITHUB_USERNAME, repo)
            
            # Create repository overview document
            repo_doc = {
                "text": create_repo_summary_text(repo_details),
                "source": "github",
                "type": "repository",
                "repo_name": repo_details["name"],
                "repo_url": repo_details["url"],
                "metadata": {
                    "full_name": repo_details["full_name"],
                    "description": repo_details["description"],
                    "primary_language": repo_details["primary_language"],
                    "languages": repo_details["languages"],
                    "language_percentages": repo_details["language_percentages"],
                    "topics": repo_details["topics"],
                    "stars": repo_details["stars"],
                    "forks": repo_details["forks"],
                    "is_private": repo_details["is_private"],
                    "is_fork": repo_details["is_fork"],
                    "is_archived": repo_details["is_archived"],
                    "license": repo_details["license"],
                    "created_at": repo_details["created_at"],
                    "updated_at": repo_details["updated_at"],
                }
            }
            documents.append(repo_doc)
            
            # Create separate README document if available
            if repo_details["readme"]:
                readme_doc = {
                    "text": repo_details["readme"],
                    "source": "github",
                    "type": "readme",
                    "repo_name": repo_details["name"],
                    "repo_url": repo_details["url"],
                    "metadata": {
                        "full_name": repo_details["full_name"],
                        "description": repo_details["description"],
                        "primary_language": repo_details["primary_language"],
                        "topics": repo_details["topics"],
                    }
                }
                documents.append(readme_doc)
            
        except Exception as e:
            logger.error(f"Failed to process repository {repo['name']}: {e}")
            continue
    
    logger.info(f"Generated {len(documents)} documents from {len(repos)} repositories")
    return documents


def create_repo_summary_text(repo_details: Dict[str, Any]) -> str:
    """Create a comprehensive text summary of a repository for embedding."""
    parts = []
    
    # Basic info
    parts.append(f"Repository: {repo_details['name']}")
    if repo_details["description"]:
        parts.append(f"Description: {repo_details['description']}")
    
    # Languages
    if repo_details["primary_language"]:
        parts.append(f"Primary Language: {repo_details['primary_language']}")
    
    if repo_details["language_percentages"]:
        lang_info = ", ".join([
            f"{lang} ({pct}%)" 
            for lang, pct in sorted(repo_details["language_percentages"].items(), 
                                  key=lambda x: x[1], reverse=True)
        ])
        parts.append(f"Languages: {lang_info}")
    
    # Topics/Tags
    if repo_details["topics"]:
        parts.append(f"Topics: {', '.join(repo_details['topics'])}")
    
    # Stats
    stats = []
    if repo_details["stars"] > 0:
        stats.append(f"{repo_details['stars']} stars")
    if repo_details["forks"] > 0:
        stats.append(f"{repo_details['forks']} forks")
    if stats:
        parts.append(f"Stats: {', '.join(stats)}")
    
    # Additional info
    if repo_details["homepage"]:
        parts.append(f"Homepage: {repo_details['homepage']}")
    
    if repo_details["license"]:
        parts.append(f"License: {repo_details['license']}")
    
    # Status flags
    flags = []
    if repo_details["is_private"]:
        flags.append("private")
    if repo_details["is_fork"]:
        flags.append("fork")
    if repo_details["is_archived"]:
        flags.append("archived")
    if flags:
        parts.append(f"Status: {', '.join(flags)}")
    
    parts.append(f"Repository URL: {repo_details['url']}")
    
    return "\n".join(parts)


if __name__ == "__main__":
    # Test the ingestion
    docs = load_github_documents()
    print(f"Generated {len(docs)} documents")
    for doc in docs[:2]:  # Show first 2 for testing
        print(f"\n--- {doc['type'].upper()}: {doc['repo_name']} ---")
        print(doc['text'][:200] + "..." if len(doc['text']) > 200 else doc['text'])