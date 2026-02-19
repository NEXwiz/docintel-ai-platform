from fastapi import APIRouter, Depends

from app.ai.retrieval import RetrievalService
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/search",
    tags=["search"]
)

retrieval_service = RetrievalService()

@router.post("/")
def semantic_search(
    query: str,
    document_id: int | None = None,
    current_user: User = Depends(get_current_user)
):
    results = retrieval_service.search(
        query = query,
        user_id = current_user.id,
        document_id = document_id
    )

    return {
        "query":query,
        "results":results
    }
