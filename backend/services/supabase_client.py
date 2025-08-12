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

from supabase import create_client, Client
from backend.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Supabase client for user management and onboarding data storage.
    """
    
    def __init__(self):
        self.supabase_url = settings.supabase_url
        self.supabase_key = settings.supabase_key
        self.client: Optional[Client] = None
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("⚠️ Supabase credentials not configured. Using stub implementation.")
        else:
            try:
                # Create client with service role key (bypasses RLS)
                self.client = create_client(self.supabase_url, self.supabase_key)
                logger.info("✅ Supabase client initialized successfully with service role key")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Supabase client: {e}")
                logger.error(f"   Make sure you're using SUPABASE_SERVICE_ROLE_KEY (not SUPABASE_ANON_KEY)")
                logger.error(f"   Falling back to stub mode.")
                self.client = None
    
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
        
        if self.client is None:
            # Fallback to stub implementation if no client
            logger.info(f"📝 [STUB] Creating user: {user_data}")
            return user_id
        
        try:
            # Insert user data into Supabase
            result = self.client.table("users").insert(user_data).execute()
            
            if result.data:
                logger.info(f"✅ User created successfully: {name} (ID: {user_id})")
                return user_id
            else:
                logger.error(f"❌ Failed to create user: No data returned")
                raise Exception("Failed to create user in database")
                
        except Exception as e:
            logger.error(f"❌ Error creating user: {e}")
            # In production, you might want to raise the exception
            # For now, we'll fall back to stub behavior
            logger.info(f"📝 [FALLBACK] Creating user: {user_data}")
            return user_id
    
    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user data by user ID.
        
        Args:
            user_id: The user ID to look up
            
        Returns:
            User data or None if not found
        """
        if self.client is None:
            logger.info(f"🔍 [STUB] Looking up user: {user_id}")
            return None
        
        try:
            result = self.client.table("users").select("*").eq("id", user_id).execute()
            
            if result.data and len(result.data) > 0:
                user_data = result.data[0]
                logger.info(f"✅ User found: {user_data['name']} (ID: {user_id})")
                return user_data
            else:
                logger.info(f"❌ User not found: {user_id}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error fetching user: {e}")
            return None
    
    async def increment_message_count(self, user_id: str) -> int:
        """
        Increment the message count for a user.
        
        Args:
            user_id: The user ID to update
            
        Returns:
            New message count
        """
        if self.client is None:
            logger.info(f"📊 [STUB] Incrementing message count for user: {user_id}")
            return 1
        
        try:
            # First get current count
            user_data = await self.get_user(user_id)
            if not user_data:
                logger.error(f"❌ Cannot increment message count: User {user_id} not found")
                return 0
            
            new_count = user_data.get("message_count", 0) + 1
            
            # Update the count
            result = self.client.table("users").update({"message_count": new_count}).eq("id", user_id).execute()
            
            if result.data:
                logger.info(f"✅ Message count updated for user {user_id}: {new_count}")
                return new_count
            else:
                logger.error(f"❌ Failed to update message count for user: {user_id}")
                return user_data.get("message_count", 0)
                
        except Exception as e:
            logger.error(f"❌ Error updating message count: {e}")
            return 1
    
    async def save_message(self, user_id: str, message: str, sender: str) -> bool:
        """
        Save a message to the messages table.
        
        Args:
            user_id: The user ID who sent or received the message
            message: The message content
            sender: Either 'user' or 'agent'
            
        Returns:
            True if message was saved successfully, False otherwise
        """
        if sender not in ['user', 'agent']:
            logger.error(f"❌ Invalid sender type: {sender}. Must be 'user' or 'agent'")
            return False
            
        message_data = {
            "user_id": user_id,
            "message": message,
            "sender": sender,
            "created_at": datetime.utcnow().isoformat()
        }
        
        if self.client is None:
            # Fallback to stub implementation if no client
            logger.info(f"💬 [STUB] Saving {sender} message for user {user_id}: {message[:50]}...")
            return True
        
        try:
            # Insert message data into Supabase
            result = self.client.table("messages").insert(message_data).execute()
            
            if result.data:
                logger.debug(f"✅ {sender.title()} message saved for user {user_id}")
                return True
            else:
                logger.error(f"❌ Failed to save {sender} message: No data returned")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error saving {sender} message: {e}")
            # In production, you might want to raise the exception
            # For now, we'll fall back to stub behavior
            logger.info(f"💬 [FALLBACK] Saving {sender} message for user {user_id}: {message[:50]}...")
            return False
    
    async def save_user_message(self, user_id: str, message: str) -> bool:
        """
        Save a user message.
        
        Args:
            user_id: The user ID who sent the message
            message: The message content
            
        Returns:
            True if message was saved successfully, False otherwise
        """
        return await self.save_message(user_id, message, "user")
    
    async def save_agent_message(self, user_id: str, message: str) -> bool:
        """
        Save an agent response message.
        
        Args:
            user_id: The user ID who received the message
            message: The agent response content
            
        Returns:
            True if message was saved successfully, False otherwise
        """
        return await self.save_message(user_id, message, "agent") 