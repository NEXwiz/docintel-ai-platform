from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.models.chat_message import ChatMessage


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatMessageIn(BaseModel):
    role: str
    content: str


class ChatMessageOut(BaseModel):
    id: int
    document_id: int
    role: str
    content: str
    created_at: str | None = None

    class Config:
        from_attributes = True


@router.get("/{document_id}", response_model=list[ChatMessageOut])
def get_chat_history(document_id: int, db: Session = Depends(get_db)):
    """Return all messages for a document, oldest first."""
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.document_id == document_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return rows


@router.post("/{document_id}", response_model=ChatMessageOut)
def save_chat_message(document_id: int, msg: ChatMessageIn, db: Session = Depends(get_db)):
    """Persist a single chat message."""
    row = ChatMessage(
        document_id=document_id,
        role=msg.role,
        content=msg.content,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{document_id}")
def clear_chat_history(document_id: int, db: Session = Depends(get_db)):
    """Delete all chat messages for a document."""
    count = (
        db.query(ChatMessage)
        .filter(ChatMessage.document_id == document_id)
        .delete()
    )
    db.commit()
    return {"deleted": count}
