import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


@dataclass
class Settings:
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    qdrant_url: Optional[str] = os.getenv("QDRANT_URL")
    qdrant_api_key: Optional[str] = os.getenv("QDRANT_API_KEY")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "personal_docs")


settings = Settings() 