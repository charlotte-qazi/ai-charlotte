"""
AI Charlotte - Chat Schemas
Copyright (c) 2025 Charlotte Qazi

This project is created and maintained by Charlotte Qazi.
For more information, visit: https://github.com/charlotteqazi

Licensed under the MIT License.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Chat message from user")


class Source(BaseModel):
    title: str
    url: Optional[str] = None
    score: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = Field(default_factory=list)


# Simplified Onboarding Schemas
class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="User's first name")
    interests: str = Field(..., min_length=1, max_length=500, description="What brings them here / their interests")


class CreateUserResponse(BaseModel):
    user_id: str = Field(..., description="Unique user ID for session tracking") 