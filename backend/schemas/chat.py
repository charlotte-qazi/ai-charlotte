from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str


class Source(BaseModel):
    title: str
    url: Optional[str] = None
    score: Optional[float] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source] = Field(default_factory=list) 