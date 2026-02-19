from qdrant_client.http.models import Filter, FieldCondition, MatchValue

from typing import List
from app.ai.vector_store import VectorStore
from app.ai.embeddings import EmbeddingService

class RetrievalService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
    
    def search(
            self,
            query: str,
            user_id: int,
            document_id: int | None = None,
            limit: int = 5
    ) -> List[str]:
        query_embedding = self.embedding_service.embed_texts([query])[0]
    
        conditions = [
            FieldCondition(
                key = "user_id",
                match = MatchValue(value = user_id)
            )
        ]

        if document_id is not None:
            conditions.append(
                FieldCondition(
                    key = "document_id",
                    match = MatchValue(value = document_id)
                )
            )
        results = self.vector_store.client.query_points(
            collection_name = self.vector_store.collection_name,
            query = query_embedding,
            limit = limit,
            with_payload = True,
            query_filter = Filter(must = conditions)
        )

        return [point.payload["text"] for point in results.points]