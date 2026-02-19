from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import UploadFile, File
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.db.session import get_db
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentCreate, DocumentResponse
from app.core.deps import get_current_user

from app.services.file_services import save_uploaded_file
from app.ai.ingestion import extract_text
from app.ai.chunking import chunk_text
from app.ai.embeddings import EmbeddingService
from app.ai.vector_store import VectorStore

embedding_service = EmbeddingService()
vector_store = VectorStore()

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

@router.post("/",response_model=DocumentResponse)
def create_document(
    document: DocumentCreate,
    current_user : User = Depends(get_current_user),
    db:Session = Depends(get_db)
):
    
    new_document = Document(
        user_id = current_user.id,
        filename = document.filename
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document

@router.get("/",response_model=list[DocumentResponse])
def list_documents(
    current_user : User = Depends(get_current_user),
    db:Session = Depends(get_db)
):

    return (db.query(Document).filter(Document.user_id == current_user.id).order_by(Document.created_at.desc()).all())

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),                    #(...) -> client must send this
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file_path = save_uploaded_file(file, current_user.id)
    text = extract_text(file_path)
    if not text or not text.strip():
        raise HTTPException(
            status_code = 400,
            detail = "No extractable text found in document"
        )

    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="Document text too short to process"
        )
    embeddings = embedding_service.embed_texts(chunks)
    
    document = Document(
        user_id = current_user.id,
        filename = file.filename
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    vector_store.upsert_chunks(
        embeddings = embeddings,
        chunks = chunks,
        user_id = current_user.id,
        document_id = document.id
    )

    return {
        "document_id":document.id,
        "chunks_stored":len(chunks)
    }

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user : User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    #Deleting vectors from qdrant
    vector_store = VectorStore()
    vector_store.client.delete(
        collection_name = vector_store.collection_name,
        points_selector = Filter(
            must=[
                FieldCondition(
                    key = "document_id",
                    match = MatchValue(value = document_id),
                ),
                FieldCondition(
                    key = "user_id",
                    match = MatchValue(value = current_user.id),
                ),
            ]
        )
    )

    db.delete(document)
    db.commit()

    return {"message":"Document Deleted"}