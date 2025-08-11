from typing import List, Tuple, Optional, Dict, Any
import hashlib
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct


class QdrantVectorStore:
    def __init__(self, url: Optional[str], api_key: Optional[str], collection: str) -> None:
        if not url:
            raise ValueError("Qdrant URL is required")
        
        self.client = QdrantClient(
            url=url,
            api_key=api_key,
        )
        self.collection = collection

    def _convert_id_to_uuid(self, string_id: str) -> str:
        """Convert a string ID to a valid UUID for Qdrant."""
        # Create a deterministic UUID from the string ID
        # This ensures the same string always produces the same UUID
        hash_object = hashlib.md5(string_id.encode())
        hash_hex = hash_object.hexdigest()
        # Convert to UUID format
        uuid_str = f"{hash_hex[:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}-{hash_hex[16:20]}-{hash_hex[20:32]}"
        return uuid_str

    def create_collection(self, vector_size: int, distance: Distance = Distance.COSINE) -> None:
        """Create a collection if it doesn't exist."""
        try:
            # Check if collection exists
            self.client.get_collection(self.collection)
            print(f"✅ Collection '{self.collection}' already exists")
        except Exception:
            # Collection doesn't exist, create it
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=vector_size, distance=distance),
            )
            print(f"✅ Created collection '{self.collection}' with vector size {vector_size}")

    def upsert(self, vectors: List[List[float]], payloads: List[Dict[str, Any]], ids: Optional[List[str]] = None) -> None:
        """Upsert embeddings into Qdrant with payloads."""
        if len(vectors) != len(payloads):
            raise ValueError("Number of vectors must match number of payloads")
        
        if ids and len(ids) != len(vectors):
            raise ValueError("Number of IDs must match number of vectors")
        
        # Generate IDs if not provided
        if not ids:
            ids = [str(i) for i in range(len(vectors))]
        
        # Convert string IDs to UUIDs that Qdrant accepts
        qdrant_ids = [self._convert_id_to_uuid(str(id_)) for id_ in ids]
        
        # Add original ID to payload for reference
        enhanced_payloads = []
        for i, payload in enumerate(payloads):
            enhanced_payload = payload.copy()
            enhanced_payload["original_id"] = ids[i]  # Store original ID in payload
            enhanced_payloads.append(enhanced_payload)
        
        # Create points
        points = [
            PointStruct(
                id=qdrant_id,
                vector=vector,
                payload=enhanced_payload
            )
            for qdrant_id, vector, enhanced_payload in zip(qdrant_ids, vectors, enhanced_payloads)
        ]
        
        # Upsert points
        self.client.upsert(
            collection_name=self.collection,
            points=points
        )
        
        print(f"✅ Upserted {len(points)} points to collection '{self.collection}'")

    def query(self, vector: List[float], top_k: int = 5, filter_conditions: Optional[Dict] = None) -> List[Tuple[float, Dict[str, Any]]]:
        """Query nearest neighbors from Qdrant."""
        search_result = self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            limit=top_k,
            query_filter=models.Filter(**filter_conditions) if filter_conditions else None
        )
        
        # Return (score, payload) tuples
        results = []
        for hit in search_result:
            results.append((hit.score, hit.payload))
        
        return results

    def count(self) -> int:
        """Get the number of points in the collection."""
        try:
            info = self.client.get_collection(self.collection)
            return info.points_count or 0
        except Exception:
            return 0

    def delete_collection(self) -> None:
        """Delete the collection (use with caution)."""
        self.client.delete_collection(self.collection)
        print(f"🗑️ Deleted collection '{self.collection}'")

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection information."""
        try:
            info = self.client.get_collection(self.collection)
            return {
                "name": self.collection,
                "points_count": info.points_count,
                "vector_size": info.config.params.vectors.size,
                "distance": info.config.params.vectors.distance.value,
                "status": info.status.value
            }
        except Exception as e:
            return {"error": str(e)} 