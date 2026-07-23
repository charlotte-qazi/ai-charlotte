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
            raise ValueError(
                "Supabase credentials not configured. "
                "Set SUPABASE_URL and SUPABASE_SERVICE_KEY in your .env file."
            )

        try:
            # Create client with service role key (bypasses RLS)
            self.client = create_client(self.supabase_url, self.supabase_key)
            logger.info("✅ Supabase client initialized successfully with service role key")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise RuntimeError(
                "Failed to initialize Supabase client. "
                "Check SUPABASE_URL and SUPABASE_SERVICE_KEY."
            ) from e

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
            "message_count": 0,
        }

        try:
            result = self.client.table("users").insert(user_data).execute()

            if result.data:
                logger.info(f"✅ User created successfully: {name} (ID: {user_id})")
                return user_id

            logger.error("❌ Failed to create user: No data returned")
            raise RuntimeError("Failed to create user in database")

        except Exception as e:
            logger.error(f"❌ Error creating user: {e}")
            raise

    async def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user data by user ID.

        Args:
            user_id: The user ID to look up

        Returns:
            User data or None if not found
        """
        try:
            result = self.client.table("users").select("*").eq("id", user_id).execute()

            if result.data and len(result.data) > 0:
                user_data = result.data[0]
                logger.info(f"✅ User found: {user_data['name']} (ID: {user_id})")
                return user_data

            logger.info(f"❌ User not found: {user_id}")
            return None

        except Exception as e:
            logger.error(f"❌ Error fetching user: {e}")
            raise

    async def increment_message_count(self, user_id: str) -> int:
        """
        Increment the message count for a user.

        Args:
            user_id: The user ID to update

        Returns:
            New message count
        """
        try:
            user_data = await self.get_user(user_id)
            if not user_data:
                logger.error(f"❌ Cannot increment message count: User {user_id} not found")
                return 0

            new_count = user_data.get("message_count", 0) + 1

            result = (
                self.client.table("users")
                .update({"message_count": new_count})
                .eq("id", user_id)
                .execute()
            )

            if result.data:
                logger.info(f"✅ Message count updated for user {user_id}: {new_count}")
                return new_count

            logger.error(f"❌ Failed to update message count for user: {user_id}")
            return user_data.get("message_count", 0)

        except Exception as e:
            logger.error(f"❌ Error updating message count: {e}")
            raise

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
        if sender not in ["user", "agent"]:
            logger.error(f"❌ Invalid sender type: {sender}. Must be 'user' or 'agent'")
            return False

        message_data = {
            "user_id": user_id,
            "message": message,
            "sender": sender,
            "created_at": datetime.utcnow().isoformat(),
        }

        try:
            result = self.client.table("messages").insert(message_data).execute()

            if result.data:
                logger.debug(f"✅ {sender.title()} message saved for user {user_id}")
                return True

            logger.error(f"❌ Failed to save {sender} message: No data returned")
            return False

        except Exception as e:
            logger.error(f"❌ Error saving {sender} message: {e}")
            raise

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
