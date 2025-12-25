"""
RAG Proxy Router - Proxies RAG requests to AI Microservice.
Handles document management and semantic search.
"""

from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging

from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.domain.auth.admin_models import AdminUser
from app.infrastructure.ai import ai_client, AIServiceError

router = APIRouter(prefix="/api/v1/rag", tags=["rag"])
logger = logging.getLogger(__name__)


# ============================================================================
# MODELS
# ============================================================================

class SearchRequest(BaseModel):
    query: str
    k: int = 5
    threshold: float = 0.5

class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total: int
    processing_time_ms: int

class DocumentInfo(BaseModel):
    id: str
    filename: str
    chunks_count: int
    uploaded_at: str
    user_id: int
    metadata: Dict[str, Any] = {}


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents(
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """List all documents indexed in RAG."""
    try:
        # Admin sees all documents or filter by user?
        # For now, let's list all documents or pass current_user.id if needed.
        # AI Client expects optional user_id
        docs = await ai_client.rag_list_documents()
        return docs
    except AIServiceError as e:
        logger.error(f"RAG list error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(default="general"),
    tags: str = Form(default=""),
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Upload document to RAG index."""
    try:
        content = await file.read()
        result = await ai_client.rag_upload_document(
            file_content=content,
            filename=file.filename,
            category=category,
            tags=tags,
            user_id=current_user.id
        )
        return result
    except AIServiceError as e:
        logger.error(f"RAG upload error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during upload")


@router.delete("/documents/{doc_id}")
async def delete_document(
    doc_id: str,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Delete document from RAG index."""
    try:
        return await ai_client.rag_delete_document(doc_id)
    except AIServiceError as e:
        logger.error(f"RAG delete error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """Semantic search in RAG documents."""
    try:
        result = await ai_client.rag_search(
            query=request.query,
            k=request.k,
            threshold=request.threshold
        )
        return result
    except AIServiceError as e:
        logger.error(f"RAG search error: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
