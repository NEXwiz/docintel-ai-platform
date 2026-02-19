from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from typing import List
import time
import uuid

class VectorStore:
    def __init__(self):
        self.collection_name = "documents"

        for _ in range(10):
            try:
                self.client = QdrantClient(host="qdrant", port=6333)
                self.client.get_collections()
                break
            except Exception:
                print("Waiting for Qdrant...")
                time.sleep(2)
        else:
            raise Exception("Qdrant not available")
        
        self._ensure_collection()

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            self.client.create_collection(
                collection_name = self.collection_name,
                vectors_config = VectorParams(
                    size = 384,
                    distance = Distance.COSINE
                )
            )
        
    def upsert_chunks(
            self,
            embeddings: List[List[str]],
            chunks: List[str],
            user_id: int,
            document_id: int
    ):
        points = []

        for vector, text in zip(embeddings,chunks):
            points.append(
                PointStruct(
                    id = str(uuid.uuid4()),
                    vector = vector,
                    payload = {
                        "user_id":user_id,
                        "document_id":document_id,
                        "text":text
                    }
                )
            )
            
        self.client.upsert(
            collection_name = self.collection_name,
            points = points
        )


