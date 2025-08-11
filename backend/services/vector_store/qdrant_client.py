from typing import List, Tuple, Optional


class QdrantVectorStore:
    def __init__(self, url: Optional[str], api_key: Optional[str], collection: str) -> None:
        self.url = url
        self.api_key = api_key
        self.collection = collection

    def upsert(self, vectors: List[List[float]], payloads: List[dict]) -> None:
        raise NotImplementedError("Upsert embeddings into Qdrant.")

    def query(self, vector: List[float], top_k: int = 5) -> List[Tuple[float, dict]]:
        raise NotImplementedError("Query nearest neighbors from Qdrant.") 