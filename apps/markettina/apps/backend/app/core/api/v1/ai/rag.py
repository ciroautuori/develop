"""
MARKETTINA v2.0 - RAG (Retrieval Augmented Generation) API Endpoints

Complete RAG functionality:
- Document upload with chunking
- Semantic search
- Context retrieval for AI
- Document management
"""
import logging
import time
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.core.security import get_api_key_header
from app.domain.rag.service import rag_service

logger = logging.getLogger(__name__)
router = APIRouter(dependencies=[Depends(get_api_key_header())])


# ============================================================================
# Request/Response Models
# ============================================================================

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    user_id: int | None = None
    k: int = Field(default=5, ge=1, le=20)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)

class SearchResultItem(BaseModel):
    text: str
    similarity: float
    metadata: dict[str, Any]
    source: str | None = None

class SearchResponse(BaseModel):
    results: list[SearchResultItem]
    total: int
    processing_time_ms: int

class ContextRequest(BaseModel):
    query: str = Field(..., min_length=1)
    max_tokens: int = Field(default=2000, ge=100, le=8000)
    user_id: int | None = None

class ContextResponse(BaseModel):
    context: str
    sources: list[str]
    processing_time_ms: int

class DocumentInfo(BaseModel):
    id: str
    filename: str
    chunks_count: int
    uploaded_at: str
    user_id: int
    metadata: dict[str, Any] = {}


# ============================================================================
# Document Upload & Management
# ============================================================================

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: int = Form(default=1),
    category: str = Form(default="general"),
    tags: str = Form(default="")
):
    """
    Upload and index a document for RAG.

    Supports: .txt, .md, .json, .csv
    """
    start = time.time()

    # Validate file type
    allowed_extensions = {".txt", ".md", ".json", ".csv", ".html"}
    file_ext = "." + (file.filename or "").split(".")[-1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {allowed_extensions}"
        )

    try:
        # Read file content
        content = await file.read()
        text_content = content.decode("utf-8")

        logger.info(
            "document_upload_start",
            filename=file.filename,
            size=len(content),
            user_id=user_id
        )

        # Prepare metadata
        metadata = {
            "category": category,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "file_type": file_ext
        }

        # Upload and index
        result = await rag_service.upload_document(
            filename=file.filename or "document",
            content=text_content,
            metadata=metadata,
            user_id=user_id
        )

        processing_time = int((time.time() - start) * 1000)
        result["processing_time_ms"] = processing_time

        return result

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="File must be UTF-8 encoded text"
        )
    except Exception as e:
        logger.error("upload_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def list_documents(user_id: int | None = None) -> list[DocumentInfo]:
    """List all indexed documents."""
    try:
        docs = await rag_service.list_documents(user_id=user_id)
        return [DocumentInfo(**doc) for doc in docs]
    except Exception as e:
        logger.error("list_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/{doc_id}")
async def get_document(doc_id: str) -> DocumentInfo:
    """Get document by ID."""
    doc = await rag_service.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentInfo(**doc)


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document and its chunks."""
    try:
        deleted = await rag_service.delete_document(doc_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"status": "deleted", "document_id": doc_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("delete_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Search & Context Retrieval
# ============================================================================

@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Semantic search across indexed documents.

    Returns ranked results by relevance.
    """
    start = time.time()

    try:
        results = await rag_service.search(
            query=request.query,
            top_k=request.k,
            min_score=request.threshold,
            user_id=request.user_id
        )

        items = [
            SearchResultItem(
                text=r.document.text,
                similarity=r.score,
                metadata=r.document.metadata,
                source=r.document.metadata.get("filename")
            )
            for r in results
        ]

        processing_time = int((time.time() - start) * 1000)

        return SearchResponse(
            results=items,
            total=len(items),
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error("search_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/context", response_model=ContextResponse)
async def get_context(request: ContextRequest):
    """
    Get context for AI content generation.

    Returns formatted context string with sources.
    """
    start = time.time()

    try:
        context = await rag_service.get_context(
            query=request.query,
            max_tokens=request.max_tokens,
            user_id=request.user_id
        )

        # Extract sources from context
        sources = []
        if context:
            import re
            source_matches = re.findall(r"\[Fonte: ([^\]]+)\]", context)
            sources = list(set(source_matches))

        processing_time = int((time.time() - start) * 1000)

        return ContextResponse(
            context=context,
            sources=sources,
            processing_time_ms=processing_time
        )

    except Exception as e:
        logger.error("context_error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Health & Status
# ============================================================================

@router.get("/")
async def rag_status():
    """RAG service status."""
    docs = await rag_service.list_documents()
    return {
        "service": "rag",
        "status": "available",
        "documents_count": len(docs),
        "vector_store": "chroma" if rag_service.vector_store else "not_initialized"
    }
