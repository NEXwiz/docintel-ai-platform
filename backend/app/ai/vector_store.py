from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from typing import List
import time
import uuid
import os


class VectorStore:
    VECTOR_SIZE = 3072

    def __init__(self):
        self.collection_name = "documents"
        self._client = None
        self._initialized = False

    @property
    def client(self) -> QdrantClient:
        """Lazy-connect to Qdrant on first use."""
        if self._client is None:
            self._connect()
        return self._client

    def _connect(self):
        url = os.getenv("QDRANT_URL")
        api_key = os.getenv("QDRANT_API_KEY")

        if url:
            print("Using Qdrant Cloud...")
            self._client = QdrantClient(
                url=url,
                api_key=api_key
            )
        else:
            print("Using Qdrant locally...")
            for _ in range(30):
                try:
                    self._client = QdrantClient(host="qdrant", port=6333)
                    self._client.get_collections()
                    break
                except Exception:
                    print("Waiting for Qdrant...")
                    time.sleep(2)
            else:
                raise Exception("Qdrant not available")

        self._ensure_collection()
        self._initialized = True

    def _ensure_collection(self):
        collections = self._client.get_collections().collections
        existing = next((c for c in collections if c.name == self.collection_name), None)

        if existing:
            # Check if dimension matches -> if not, recreate
            try:
                info = self._client.get_collection(self.collection_name)
                current_size = info.config.params.vectors.size
                if current_size != self.VECTOR_SIZE:
                    print(f"Collection dimension mismatch ({current_size} vs {self.VECTOR_SIZE}), recreating...")
                    self._client.delete_collection(self.collection_name)
                else:
                    self._ensure_indexes()
                    return
            except Exception:
                pass

        self._client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create payload indexes required for filtered queries."""
        from qdrant_client.http.models import PayloadSchemaType
        for field in ("user_id", "document_id"):
            try:
                self._client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field,
                    field_schema=PayloadSchemaType.INTEGER,
                )
            except Exception:
                pass  # Index already exists

    def upsert_chunks(
            self,
            embeddings: List[List[float]],
            chunks: List[str],
            user_id: int,
            document_id: int
    ):
        points = []

        for vector, text in zip(embeddings, chunks):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "user_id": user_id,
                        "document_id": document_id,
                        "text": text
                    }
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def upsert_parent_child_chunks(
            self,
            embeddings: List[List[float]],
            parent_child_data: List[dict],
            user_id: int,
            document_id: int
    ):
        """
        Upsert chunks with parent-child relationship.
        Each point stores child_text (for search) and parent_text (for LLM context).

        Args:
            embeddings: Embeddings for the child chunks.
            parent_child_data: List of dicts from create_parent_child_chunks().
            user_id: The user who owns the document.
            document_id: The document ID.
        """
        points = []

        for vector, pc_data in zip(embeddings, parent_child_data):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={
                        "user_id": user_id,
                        "document_id": document_id,
                        "text": pc_data["child_text"],
                        "parent_text": pc_data["parent_text"],
                        "parent_id": pc_data["parent_id"],
                    }
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
