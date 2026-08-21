from fastapi import APIRouter

from app.ai.retrieval  import RetrievalService
from app.ai.llm import LLMService

# Default user ID (auth removed — RAG-focused development)
DEFAULT_USER_ID = 1

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
):
    chunks = retrieval_service.search(
        query = query,
        user_id = DEFAULT_USER_ID,
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