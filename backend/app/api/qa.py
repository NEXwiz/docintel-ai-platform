from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
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


def _retrieve_context_and_history(query, document_id, db):
    """Shared logic: retrieve chunks + fetch chat history."""
    chunks = retrieval_service.search(
        query=query,
        user_id=DEFAULT_USER_ID,
        document_id=document_id
    )

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

    return chunks, chat_history


@router.post("/")
def ask_question(
    query: str,
    document_id: int | None = None,
    db: Session = Depends(get_db),
):
    try:
        chunks, chat_history = _retrieve_context_and_history(query, document_id, db)

        if not chunks:
            return {
                "query": query,
                "answer": "No relevant content found in this document for your question.",
                "sources": []
            }

        context = "\n\n".join(chunks)

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


@router.post("/stream")
def ask_question_stream(
    query: str,
    document_id: int | None = None,
    db: Session = Depends(get_db),
):
    """Stream answer tokens via Server-Sent Events."""
    chunks, chat_history = _retrieve_context_and_history(query, document_id, db)

    if not chunks:
        def no_content():
            yield "data: No relevant content found in this document for your question.\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(no_content(), media_type="text/event-stream")

    context = "\n\n".join(chunks)

    def event_generator():
        for token in llm_service.generate_answer_stream(
            query=query,
            context=context,
            chat_history=chat_history,
        ):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")