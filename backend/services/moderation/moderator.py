"""
AI Charlotte - OpenAI Moderation Service
Copyright (c) 2025 Charlotte Qazi

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from openai import AsyncOpenAI
from backend.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ModerationResult:
    """Result from content moderation."""
    is_flagged: bool
    categories: Dict[str, bool]
    category_scores: Dict[str, float]
    reason: Optional[str] = None


class ModerationService:
    """
    OpenAI-based content moderation service.
    
    Checks user messages for harmful content using OpenAI's moderation API
    before they are processed by the RAG system.
    """
    
    def __init__(self):
        """Initialize the moderation service with OpenAI client."""
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key is required for moderation service")
        
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._enabled = getattr(settings, 'moderation_enabled', True)
        
    async def moderate_content(self, content: str) -> ModerationResult:
        """
        Check if content violates OpenAI's usage policies.
        
        Args:
            content: The text content to moderate
            
        Returns:
            ModerationResult with flagged status and details
        """
        if not self._enabled:
            logger.info("🟡 Moderation is disabled, allowing content")
            return ModerationResult(
                is_flagged=False,
                categories={},
                category_scores={}
            )
        
        if not content or len(content.strip()) == 0:
            logger.warning("⚠️ Empty content provided for moderation")
            return ModerationResult(
                is_flagged=False,
                categories={},
                category_scores={}
            )
        
        try:
            logger.debug(f"🔍 Moderating content: {content[:50]}...")
            
            response = await self.client.moderations.create(
                input=content,
                model="text-moderation-latest"
            )
            
            result = response.results[0]
            
            # Determine reason for flagging
            reason = None
            if result.flagged:
                flagged_categories = [
                    category for category, flagged in result.categories.model_dump().items() 
                    if flagged
                ]
                reason = f"Content flagged for: {', '.join(flagged_categories)}"
                logger.warning(f"🚫 Content moderation flagged: {reason}")
            else:
                logger.info("✅ Content passed moderation check")
            
            return ModerationResult(
                is_flagged=result.flagged,
                categories=result.categories.model_dump(),
                category_scores=result.category_scores.model_dump(),
                reason=reason
            )
            
        except Exception as e:
            logger.error(f"❌ Moderation API error: {e}")
            
            # In case of API failure, we have options:
            # 1. Fail closed (reject all content) - more secure
            # 2. Fail open (allow all content) - better user experience
            
            # We'll fail open but log the incident for monitoring
            if getattr(settings, 'moderation_fail_closed', False):
                return ModerationResult(
                    is_flagged=True,
                    categories={},
                    category_scores={},
                    reason="Moderation service temporarily unavailable"
                )
            else:
                # Fail open - allow content but log the error
                return ModerationResult(
                    is_flagged=False,
                    categories={},
                    category_scores={},
                    reason="Moderation check skipped due to service error"
                )
    
    async def is_content_safe(self, content: str) -> bool:
        """
        Simple boolean check for content safety.
        
        Args:
            content: The text content to check
            
        Returns:
            True if content is safe, False if flagged
        """
        result = await self.moderate_content(content)
        return not result.is_flagged
    
    def is_enabled(self) -> bool:
        """Check if moderation is enabled."""
        return self._enabled
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Health check for the moderation service.
        
        Returns:
            Health status information
        """
        try:
            # Test with safe content
            test_result = await self.moderate_content("Hello, how are you today?")
            
            return {
                "status": "healthy",
                "enabled": self._enabled,
                "api_available": True,
                "test_passed": not test_result.is_flagged
            }
        except Exception as e:
            logger.error(f"❌ Moderation health check failed: {e}")
            return {
                "status": "unhealthy",
                "enabled": self._enabled,
                "api_available": False,
                "error": str(e)
            } 