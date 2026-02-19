from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models.user import User
from app.ai.retrieval  import RetrievalService
from app.ai.llm import LLMService

router = APIRouter(
    prefix="/qa",
    tags=["Q&A"]
)

retrieval_service = RetrievalService()
llm_service = LLMService()

@router.post("/")
def ask_question(
    query: str,
    document_id: int | None = None,
    current_user: User = Depends(get_current_user)
):
    chunks = retrieval_service.search(
        query = query,
        user_id = current_user.id,
        document_id = document_id
    )

    context = "\n\n".join(chunks)

    answer = llm_service.generate_answer(
        query = query,
        context = context
    )

    return {
        "query":query,
        "answer":answer,
        "sources":chunks
    }