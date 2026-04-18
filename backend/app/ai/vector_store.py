from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from typing import List
import time
import uuid
import os


class VectorStore:
    def __init__(self):
        self.collection_name = "documents"

        url = os.getenv("QDRANT_URL")
        api_key = os.getenv("QDRANT_API_KEY")

        if url:
            print("Using Qdrant Cloud...")
            self.client = QdrantClient(
                url = url,
                api_key = api_key
            )

        else:
            print("Using Qdrant locally...")
            for _ in range(30):
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

    VECTOR_SIZE = 768

    def _ensure_collection(self):
        collections = self.client.get_collections().collections
        existing = next((c for c in collections if c.name == self.collection_name), None)

        if existing:
            # Check if dimension matches; if not, recreate
            try:
                info = self.client.get_collection(self.collection_name)
                current_size = info.config.params.vectors.size
                if current_size != self.VECTOR_SIZE:
                    print(f"Collection dimension mismatch ({current_size} vs {self.VECTOR_SIZE}), recreating...")
                    self.client.delete_collection(self.collection_name)
                else:
                    return
            except Exception:
                pass

        self.client.create_collection(
            collection_name = self.collection_name,
            vectors_config = VectorParams(
                size = self.VECTOR_SIZE,
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


