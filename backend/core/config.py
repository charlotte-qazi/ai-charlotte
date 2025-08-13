"""
AI Charlotte - Configuration Management
Copyright (c) 2025 Charlotte Qazi

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


@dataclass
class Settings:
    # API Keys
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    qdrant_url: Optional[str] = os.getenv("QDRANT_URL")
    qdrant_api_key: Optional[str] = os.getenv("QDRANT_API_KEY")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "personal_docs")
    github_username: Optional[str] = os.getenv("GITHUB_USERNAME")
    github_api_token: Optional[str] = os.getenv("GITHUB_API_TOKEN")
    
    # Supabase Configuration
    supabase_url: Optional[str] = os.getenv("SUPABASE_URL")
    supabase_key: Optional[str] = os.getenv("SUPABASE_SERVICE_KEY")  # Use service role key for server-side operations
    supabase_anon_key: Optional[str] = os.getenv("SUPABASE_ANON_KEY")  # Keep anon key for reference
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    
    # Environment Configuration
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # CORS Configuration
    cors_origins: List[str] = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","))
    
    # Rate Limiting
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
    
    # Content Moderation Configuration
    moderation_enabled: bool = os.getenv("MODERATION_ENABLED", "true").lower() == "true"
    moderation_fail_closed: bool = os.getenv("MODERATION_FAIL_CLOSED", "false").lower() == "true"  # Whether to block content when moderation API fails
    
    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


settings = Settings() 