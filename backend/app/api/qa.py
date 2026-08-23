from fastapi import APIRouter, HTTPException

from app.ai.retrieval import RetrievalService
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
    try:
        chunks = retrieval_service.search(
            query=query,
            user_id=DEFAULT_USER_ID,
            document_id=document_id
        )

        if not chunks:
            return {
                "query": query,
                "answer": "No relevant content found in this document for your question.",
                "sources": []
            }

        context = "\n\n".join(chunks)

        answer = llm_service.generate_answer(
            query=query,
            context=context
        )

        return {
            "query": query,
            "answer": answer,
            "sources": chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))