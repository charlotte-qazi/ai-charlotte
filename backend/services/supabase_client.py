"""
AI Charlotte - Supabase Client Service
Copyright (c) 2025 Charlotte Qazi

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from backend.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Simplified Supabase client for user management.
    For now, this is a stub implementation that logs data instead of actually storing it.
    """
    
    def __init__(self):
        self.supabase_url = settings.supabase_url
        self.supabase_key = settings.supabase_key
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("⚠️ Supabase credentials not configured. Using stub implementation.")
    
    async def create_user(self, name: str, interests: str) -> str:
        """
        Create a new user with onboarding data.
        
        Args:
            name: User's first name
            interests: What brings them here / their interests
            
        Returns:
            User ID for session tracking
        """
        user_id = str(uuid.uuid4())
        
        user_data = {
            "id": user_id,
            "name": name,
            "interests": interests,
            "created_at": datetime.utcnow().isoformat(),
            "message_count": 0
        }
        
        # TODO: Replace with actual Supabase insertion
        logger.info(f"📝 [STUB] Creating user: {user_data}")
        
        # For now, we'll just return the user ID
        # In a real implementation, this would:
        # 1. Insert the data into Supabase users table
        # 2. Handle any database errors
        # 3. Return the actual user ID from the database
        
        return user_id
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user data by user ID.
        
        Args:
            user_id: The user ID to look up
            
        Returns:
            User data or None if not found
        """
        # TODO: Replace with actual Supabase query
        logger.info(f"🔍 [STUB] Looking up user: {user_id}")
        
        # For now, return a stub response
        # In a real implementation, this would query the Supabase users table
        return None
    
    async def increment_message_count(self, user_id: str) -> int:
        """
        Increment the message count for a user.
        
        Args:
            user_id: The user ID to update
            
        Returns:
            New message count
        """
        # TODO: Replace with actual Supabase update
        logger.info(f"📊 [STUB] Incrementing message count for user: {user_id}")
        
        # For now, return a stub count
        # In a real implementation, this would:
        # 1. Update the message_count in Supabase
        # 2. Return the new count
        return 1 