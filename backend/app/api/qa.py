from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.ai.retrieval import RetrievalService
from app.ai.llm import LLMService
from app.db.session import get_db
from app.models.chat_message import ChatMessage

# Default user ID (auth removed — RAG-focused development)
DEFAULT_USER_ID = 1
MAX_HISTORY = 10

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
    db: Session = Depends(get_db),
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

        # Fetch recent chat history for multi-turn context
        chat_history = []
        if document_id is not None:
            rows = (
                db.query(ChatMessage)
                .filter(ChatMessage.document_id == document_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(MAX_HISTORY)
                .all()
            )
            chat_history = [
                {"role": r.role, "content": r.content}
                for r in reversed(rows)
            ]

        answer = llm_service.generate_answer(
            query=query,
            context=context,
            chat_history=chat_history,
        )

        return {
            "query": query,
            "answer": answer,
            "sources": chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))