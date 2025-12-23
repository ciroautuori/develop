"""
Admin Inbox Router - Email Management API
Endpoints per leggere e gestire email via IMAP
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.infrastructure.email import get_imap_service, EmailMessage, EmailFolder
from app.core.api.dependencies.auth_deps import get_current_admin_user

router = APIRouter(prefix="/inbox", tags=["Admin Inbox"])


# =============================================================================
# SCHEMAS
# =============================================================================

class EmailAttachmentResponse(BaseModel):
    """Attachment response."""
    filename: str
    content_type: str
    size: int


class EmailResponse(BaseModel):
    """Email response."""
    id: str
    subject: str
    from_email: str
    from_name: Optional[str]
    to_email: str
    date: datetime
    body_text: Optional[str]
    body_html: Optional[str]
    is_read: bool
    is_starred: bool
    attachments: List[EmailAttachmentResponse]
    folder: str

    class Config:
        from_attributes = True


class EmailListResponse(BaseModel):
    """Email list response with pagination."""
    emails: List[EmailResponse]
    total: int
    unread: int
    limit: int
    offset: int


class FolderResponse(BaseModel):
    """Folder response."""
    name: str
    display_name: str
    total: int
    unread: int


class ConnectionStatusResponse(BaseModel):
    """Connection status response."""
    connected: bool
    server: Optional[str] = None
    username: Optional[str] = None
    inbox_total: Optional[int] = None
    inbox_unread: Optional[int] = None
    error: Optional[str] = None


class MarkReadRequest(BaseModel):
    """Mark as read request."""
    msg_id: str
    folder: str = "INBOX"
    read: bool = True


class MoveEmailRequest(BaseModel):
    """Move email request."""
    msg_id: str
    from_folder: str
    to_folder: str


class StarEmailRequest(BaseModel):
    """Star email request."""
    msg_id: str
    folder: str = "INBOX"
    starred: bool = True


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def email_to_response(email: EmailMessage) -> EmailResponse:
    """Convert EmailMessage to response."""
    return EmailResponse(
        id=email.id,
        subject=email.subject,
        from_email=email.from_email,
        from_name=email.from_name,
        to_email=email.to_email,
        date=email.date,
        body_text=email.body_text,
        body_html=email.body_html,
        is_read=email.is_read,
        is_starred=email.is_starred,
        attachments=[
            EmailAttachmentResponse(
                filename=att.filename,
                content_type=att.content_type,
                size=att.size
            )
            for att in email.attachments
        ],
        folder=email.folder
    )


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/status", response_model=ConnectionStatusResponse)
async def get_connection_status(
    current_user = Depends(get_current_admin_user)
):
    """
    Test IMAP connection and get inbox stats.
    """
    service = get_imap_service()
    result = await service.test_connection()
    return ConnectionStatusResponse(**result)


@router.get("/folders", response_model=List[FolderResponse])
async def get_folders(
    current_user = Depends(get_current_admin_user)
):
    """
    Get list of email folders.
    """
    service = get_imap_service()
    folders = await service.get_folders()
    return [
        FolderResponse(
            name=f.name,
            display_name=f.display_name,
            total=f.total,
            unread=f.unread
        )
        for f in folders
    ]


@router.get("/emails", response_model=EmailListResponse)
async def get_emails(
    folder: str = Query("INBOX", description="Folder name"),
    limit: int = Query(50, ge=1, le=100, description="Max emails to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    search: Optional[str] = Query(None, description="Search query"),
    unread_only: bool = Query(False, description="Only unread emails"),
    current_user = Depends(get_current_admin_user)
):
    """
    Get emails from folder with pagination.
    """
    service = get_imap_service()

    try:
        result = await service.get_emails(
            folder=folder,
            limit=limit,
            offset=offset,
            search_query=search,
            unread_only=unread_only
        )

        return EmailListResponse(
            emails=[email_to_response(e) for e in result["emails"]],
            total=result["total"],
            unread=result["unread"],
            limit=result["limit"],
            offset=result["offset"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch emails: {str(e)}")


@router.get("/emails/{msg_id}", response_model=EmailResponse)
async def get_email(
    msg_id: str,
    folder: str = Query("INBOX", description="Folder name"),
    current_user = Depends(get_current_admin_user)
):
    """
    Get single email by ID.
    """
    service = get_imap_service()

    email = await service.get_email(msg_id, folder)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    return email_to_response(email)


@router.post("/emails/mark-read")
async def mark_email_read(
    request: MarkReadRequest,
    current_user = Depends(get_current_admin_user)
):
    """
    Mark email as read or unread.
    """
    service = get_imap_service()

    if request.read:
        success = await service.mark_as_read(request.msg_id, request.folder)
    else:
        success = await service.mark_as_unread(request.msg_id, request.folder)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update email")

    return {"success": True, "msg_id": request.msg_id, "is_read": request.read}


@router.post("/emails/star")
async def star_email(
    request: StarEmailRequest,
    current_user = Depends(get_current_admin_user)
):
    """
    Star or unstar email.
    """
    service = get_imap_service()

    success = await service.toggle_star(request.msg_id, request.starred, request.folder)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update email")

    return {"success": True, "msg_id": request.msg_id, "is_starred": request.starred}


@router.post("/emails/move")
async def move_email(
    request: MoveEmailRequest,
    current_user = Depends(get_current_admin_user)
):
    """
    Move email to another folder.
    """
    service = get_imap_service()

    success = await service.move_email(
        request.msg_id,
        request.from_folder,
        request.to_folder
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to move email")

    return {"success": True, "msg_id": request.msg_id, "moved_to": request.to_folder}


@router.delete("/emails/{msg_id}")
async def delete_email(
    msg_id: str,
    folder: str = Query("INBOX", description="Folder name"),
    current_user = Depends(get_current_admin_user)
):
    """
    Delete email (move to trash).
    """
    service = get_imap_service()

    success = await service.delete_email(msg_id, folder)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete email")

    return {"success": True, "msg_id": msg_id, "deleted": True}
