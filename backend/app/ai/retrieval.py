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
            limit: int = 5,
            score_threshold: float = 0.3,
            use_parent_context: bool = True,
    ) -> List[str]:
        """
        Semantic search with optional parent-child retrieval.

        Args:
            query: The user's question.
            user_id: Current user ID (for multi-tenant filtering).
            document_id: Optional document filter.
            limit: Max results to return.
            score_threshold: Minimum cosine similarity score (0-1). Results
                below this threshold are discarded.
            use_parent_context: If True and parent_text exists in payload,
                return parent chunks instead of child chunks for richer LLM context.

        Returns:
            List of text strings (parent or child chunks depending on settings).
        """
        query_embedding = self.embedding_service.embed_texts([query])[0]

        conditions = [
            FieldCondition(
                key="user_id",
                match=MatchValue(value=user_id)
            )
        ]

        if document_id is not None:
            conditions.append(
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            )

        results = self.vector_store.client.query_points(
            collection_name=self.vector_store.collection_name,
            query=query_embedding,
            limit=limit,
            with_payload=True,
            query_filter=Filter(must=conditions),
            score_threshold=score_threshold,
        )

        if not results.points:
            return []

        # If using parent-child retrieval, deduplicate parent chunks
        if use_parent_context:
            seen_parents = set()
            parent_chunks = []
            for point in results.points:
                parent_text = point.payload.get("parent_text")
                if parent_text:
                    parent_id = point.payload.get("parent_id", parent_text[:50])
                    if parent_id not in seen_parents:
                        seen_parents.add(parent_id)
                        parent_chunks.append(parent_text)
                else:
                    # No parent — use the child text directly
                    parent_chunks.append(point.payload["text"])
            return parent_chunks

        return [point.payload["text"] for point in results.points]