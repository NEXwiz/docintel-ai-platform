from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi import UploadFile, File
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.db.session import get_db
from app.models.document import Document
from app.schemas.document import DocumentCreate, DocumentResponse

from app.services.file_services import save_uploaded_file
from app.ai.ingestion import extract_with_format
from app.ai.chunking import smart_chunk, create_parent_child_chunks
from app.ai.embeddings import EmbeddingService
from app.ai.vector_store import VectorStore

# Default user ID (auth removed — RAG-focused development)
DEFAULT_USER_ID = 1

embedding_service = EmbeddingService()
vector_store = VectorStore()

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

@router.post("/",response_model=DocumentResponse)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db)
):

    new_document = Document(
        user_id = DEFAULT_USER_ID,
        filename = document.filename
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return new_document

@router.get("/",response_model=list[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db)
):

    return (db.query(Document).filter(Document.user_id == DEFAULT_USER_ID).order_by(Document.created_at.desc()).all())

@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    chunk_size: int = Query(200, ge=50, le=1000, description="Target chunk size in tokens"),
    chunking_method: str = Query("auto", description="Chunking method: auto, structural, semantic"),
    use_parent_child: bool = Query(False, description="Use parent-child chunking for better retrieval"),
):
    file_path = save_uploaded_file(file, DEFAULT_USER_ID)
    text, format_tag = extract_with_format(file_path)
    if not text or not text.strip():
        raise HTTPException(
            status_code = 400,
            detail = "No extractable text found in document"
        )

    # Create document record FIRST so we can rollback if vectorization fails
    document = Document(
        user_id = DEFAULT_USER_ID,
        filename = file.filename
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        if use_parent_child:
            # Parent-child chunking: small chunks for search, big chunks for LLM
            pc_data = create_parent_child_chunks(
                text,
                parent_size=chunk_size * 2,
                child_size=chunk_size,
                format_tag=format_tag,
            )
            if not pc_data:
                raise HTTPException(status_code=400, detail="Document text too short to process")

            child_texts = [pc["child_text"] for pc in pc_data]
            embeddings = embedding_service.embed_texts(child_texts)

            vector_store.upsert_parent_child_chunks(
                embeddings=embeddings,
                parent_child_data=pc_data,
                user_id=DEFAULT_USER_ID,
                document_id=document.id
            )

            return {
                "document_id": document.id,
                "chunks_stored": len(pc_data),
                "method": "parent_child",
                "format": format_tag,
            }
        else:
            # Standard chunking with format-awareness
            chunks = smart_chunk(
                text,
                format_tag=format_tag,
                chunk_size=chunk_size,
                method=chunking_method,
            )
            if not chunks:
                raise HTTPException(status_code=400, detail="Document text too short to process")

            embeddings = embedding_service.embed_texts(chunks)

            vector_store.upsert_chunks(
                embeddings=embeddings,
                chunks=chunks,
                user_id=DEFAULT_USER_ID,
                document_id=document.id
            )

            return {
                "document_id": document.id,
                "chunks_stored": len(chunks),
                "method": chunking_method,
                "format": format_tag,
            }

    except HTTPException:
        raise
    except Exception as e:
        # Rollback DB record if vectorization fails
        db.delete(document)
        db.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    document = (
        db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == DEFAULT_USER_ID
        )
        .first()
    )

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    #Deleting vectors from qdrant
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
                    match = MatchValue(value = DEFAULT_USER_ID),
                ),
            ]
        )
    )

    db.delete(document)
    db.commit()

    return {"message":"Document Deleted"}