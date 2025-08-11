from typing import List, Optional


class EmbeddingClient:
    def __init__(self, api_key: Optional[str], model: str = "text-embedding-3-small") -> None:
        self.api_key = api_key
        self.model = model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("Call OpenAI embeddings API here.") 