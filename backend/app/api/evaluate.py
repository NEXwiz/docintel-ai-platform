"""
Chunk evaluation endpoint.
Lets you preview how a document will be chunked before committing.
"""

from fastapi import APIRouter, UploadFile, File, Query, HTTPException

from app.ai.ingestion import extract_with_format
from app.ai.chunking import smart_chunk, _count_tokens

router = APIRouter(
    prefix="/evaluate",
    tags=["Evaluation"]
)


@router.post("/chunking")
def evaluate_chunking(
    file: UploadFile = File(...),
    chunk_size: int = Query(200, ge=50, le=1000),
    chunking_method: str = Query("auto"),
):
    """
    Preview how a document will be chunked without storing anything.

    Returns chunk stats and a preview of the first 5 chunks.
    """
    import tempfile
    import os

    # Save to temp location
    ext = os.path.splitext(file.filename)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(file.file.read())
        tmp_path = tmp.name

    try:
        text, format_tag = extract_with_format(tmp_path)

        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="No extractable text found")

        chunks = smart_chunk(
            text,
            format_tag=format_tag,
            chunk_size=chunk_size,
            method=chunking_method,
        )

        if not chunks:
            raise HTTPException(status_code=400, detail="Document too short to chunk")

        # Compute stats
        token_counts = [_count_tokens(c) for c in chunks]
        total_tokens = sum(token_counts)
        avg_tokens = total_tokens / len(token_counts) if token_counts else 0
        min_tokens = min(token_counts) if token_counts else 0
        max_tokens = max(token_counts) if token_counts else 0

        return {
            "filename": file.filename,
            "format": format_tag,
            "method": chunking_method,
            "chunk_size_setting": chunk_size,
            "stats": {
                "total_chunks": len(chunks),
                "total_tokens": total_tokens,
                "avg_tokens_per_chunk": round(avg_tokens, 1),
                "min_tokens": min_tokens,
                "max_tokens": max_tokens,
                "token_distribution": token_counts,
            },
            "preview": [
                {
                    "index": i,
                    "tokens": _count_tokens(c),
                    "text": c[:500] + ("..." if len(c) > 500 else "")
                }
                for i, c in enumerate(chunks[:5])
            ]
        }
    finally:
        os.unlink(tmp_path)
