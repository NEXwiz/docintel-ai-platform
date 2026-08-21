from fastapi import APIRouter

from app.ai.retrieval import RetrievalService

# Default user ID (auth removed — RAG-focused development)
DEFAULT_USER_ID = 1

router = APIRouter(
    prefix="/search",
    tags=["search"]
)

retrieval_service = RetrievalService()

@router.post("/")
def semantic_search(
    query: str,
    document_id: int | None = None,
):
    results = retrieval_service.search(
        query = query,
        user_id = DEFAULT_USER_ID,
        document_id = document_id
    )

    return {
        "query":query,
        "results":results
    }
