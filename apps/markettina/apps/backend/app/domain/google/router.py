"""
Google Integrations Router - Admin endpoints for GA4 and GMB
"""
import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.core.config import settings
from app.domain.auth.admin_models import AdminUser
from app.infrastructure.database.session import get_db

from .analytics_service import GoogleAnalyticsService
from .business_profile_service import GoogleBusinessProfileService
from .models import AdminGoogleSettings
from .schemas import (
    GADashboardResponse,
    GAOverviewMetrics,
    GMBDashboardResponse,
    GMBPostCreate,
    GMBPostsResponse,
    GMBReviewReplyRequest,
    GMBReviewsResponse,
    GoogleConnectionStatus,
    GooglePropertySelect,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/admin/google", tags=["google-integrations"])


# ============================================================================
# SCHEMAS
# ============================================================================

class GAPropertiesResponse(BaseModel):
    """List of GA4 properties."""
    accounts: list[dict] = []
    properties: list[dict] = []


class GMBLocationsResponse(BaseModel):
    """List of GMB locations."""
    accounts: list[dict] = []
    locations: list[dict] = []


# ============================================================================
# OAUTH ENDPOINTS - Using unified Google OAuth service
# ============================================================================

from app.core.google import google_oauth_service


@router.get("/connect")
async def initiate_google_connect(
    request: Request,
    admin: AdminUser = Depends(get_current_admin_user)
):
    """
    Initiate Google OAuth flow with extended scopes.
    Uses unified service with 'backoffice_full' scope set (Analytics, Business, Calendar, Search Console, Gmail, Drive).
    """
    # Generate CSRF state with admin ID embedded
    state = google_oauth_service.generate_csrf_state(extra_data=str(admin.id))

    # Build redirect URI for admin connection
    redirect_uri = google_oauth_service.get_default_redirect_uri("admin")

    # Generate auth URL using unified service with full admin scopes
    google_auth_url = google_oauth_service.get_auth_url(
        redirect_uri=redirect_uri,
        use_case="backoffice_full",  # Analytics + Business + Calendar + Search Console + Gmail + Drive
        state=state,
    )

    logger.info(f"Initiating Google OAuth for admin {admin.id}")
    return {"auth_url": google_auth_url, "state": state.split(":")[0]}


@router.get("/callback")
async def google_oauth_callback(
    request: Request,
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db),
):
    """
    Handle Google OAuth callback.
    Uses unified service to exchange code and store tokens.
    """
    if error:
        logger.error(f"Google OAuth error: {error}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/admin/settings?google_error={error}",
            status_code=302
        )

    if not code or not state:
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/admin/settings?google_error=missing_code",
            status_code=302
        )

    try:
        # Parse state to extract admin ID
        state_data = google_oauth_service.parse_csrf_state(state)
        if not state_data.get("extra"):
            raise ValueError("Invalid state format - missing admin ID")
        admin_id = int(state_data["extra"])

        # Exchange code for tokens using unified service
        redirect_uri = google_oauth_service.get_default_redirect_uri("admin")
        token_response = await google_oauth_service.exchange_code(
            code=code,
            redirect_uri=redirect_uri,
        )

        if not token_response:
            logger.error("Token exchange failed")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/admin/settings?google_error=token_exchange_failed",
                status_code=302
            )

        access_token = token_response.access_token
        refresh_token = token_response.refresh_token
        expires_in = token_response.expires_in
        scope = token_response.scope

        # Calculate expiration time
        expires_at = datetime.now(UTC) + timedelta(seconds=expires_in)

        # Store or update settings
        google_settings = db.query(AdminGoogleSettings).filter(
            AdminGoogleSettings.admin_id == admin_id
        ).first()

        if not google_settings:
            google_settings = AdminGoogleSettings(admin_id=admin_id)
            db.add(google_settings)

        google_settings.access_token = access_token
        if refresh_token:
            google_settings.refresh_token = refresh_token
        google_settings.token_expires_at = expires_at
        google_settings.scopes = scope
        google_settings.updated_at = datetime.now(UTC)

        db.commit()

        logger.info(f"Google OAuth connected for admin {admin_id} - scopes: {scope}")

        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/admin/settings?google_connected=true",
            status_code=302
        )

    except Exception as e:
        logger.error(f"Google OAuth callback error: {e}", exc_info=True)
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/admin/settings?google_error=callback_failed",
            status_code=302
        )


@router.get("/status", response_model=GoogleConnectionStatus)
async def get_google_connection_status(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get current Google integration connection status."""
    from app.core.google import GoogleTokenManager

    google_settings = db.query(AdminGoogleSettings).filter(
        AdminGoogleSettings.admin_id == admin.id
    ).first()

    if not google_settings or not google_settings.access_token:
        return GoogleConnectionStatus()

    # Use GoogleTokenManager to get valid token (auto-refreshes if expired)
    token_manager = GoogleTokenManager(db)
    valid_token = await token_manager.get_valid_token(admin_id=admin.id)

    # If token manager returns None, token refresh failed
    is_connected = valid_token is not None

    scopes = google_settings.scopes or ""

    return GoogleConnectionStatus(
        analytics_connected="analytics.readonly" in scopes and is_connected,
        business_profile_connected="business.manage" in scopes and is_connected,
        analytics_property_id=google_settings.ga4_property_id,
        business_account_id=google_settings.gmb_account_id,
        business_location_id=google_settings.gmb_location_id,
        last_sync=google_settings.updated_at,
        token_expires_at=google_settings.token_expires_at
    )


@router.post("/disconnect")
async def disconnect_google(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Disconnect Google integration."""
    google_settings = db.query(AdminGoogleSettings).filter(
        AdminGoogleSettings.admin_id == admin.id
    ).first()

    if google_settings:
        google_settings.access_token = None
        google_settings.refresh_token = None
        google_settings.token_expires_at = None
        google_settings.scopes = None
        db.commit()

    logger.info(f"Google disconnected successfully for admin {admin.id}")

    return {"message": "Google disconnected successfully"}


# ============================================================================
# GOOGLE ANALYTICS ENDPOINTS
# ============================================================================

async def get_analytics_service(
    db: Session,
    admin: AdminUser
) -> GoogleAnalyticsService:
    """Get configured GA4 service for admin."""
    from app.core.google import GoogleTokenManager

    google_settings = db.query(AdminGoogleSettings).filter(
        AdminGoogleSettings.admin_id == admin.id
    ).first()

    if not google_settings or not google_settings.access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google Analytics not connected. Please connect your Google account."
        )

    # Use GoogleTokenManager to get valid token (auto-refreshes if expired)
    token_manager = GoogleTokenManager(db)
    valid_token_data = await token_manager.get_valid_token(admin_id=admin.id)

    if not valid_token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google token expired and refresh failed. Please reconnect your Google account."
        )

    property_id = google_settings.ga4_property_id or "properties/467399370"  # Default property

    return GoogleAnalyticsService(
        access_token=valid_token_data["access_token"],
        property_id=property_id
    )


@router.get("/analytics/dashboard", response_model=GADashboardResponse)
async def get_analytics_dashboard(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get complete GA4 dashboard data."""
    service = await get_analytics_service(db, admin)
    return await service.get_full_dashboard(days=days)


@router.get("/analytics/overview", response_model=GAOverviewMetrics)
async def get_analytics_overview(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get overview metrics for GA4."""
    service = await get_analytics_service(db, admin)
    return await service.get_overview_metrics(days=days)


@router.get("/analytics/traffic")
async def get_analytics_traffic(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get daily traffic data."""
    service = await get_analytics_service(db, admin)
    return await service.get_daily_traffic(days=days)


@router.get("/analytics/sources")
async def get_analytics_sources(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get traffic sources."""
    service = await get_analytics_service(db, admin)
    return await service.get_traffic_sources(days=days, limit=limit)


@router.get("/analytics/pages")
async def get_analytics_top_pages(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get top pages."""
    service = await get_analytics_service(db, admin)
    return await service.get_top_pages(days=days, limit=limit)


@router.get("/analytics/devices")
async def get_analytics_devices(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get device breakdown."""
    service = await get_analytics_service(db, admin)
    return await service.get_device_breakdown(days=days)


@router.get("/analytics/geo")
async def get_analytics_geo(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get geographic data."""
    service = await get_analytics_service(db, admin)
    return await service.get_geographic_data(days=days, limit=limit)


@router.get("/analytics/properties", response_model=GAPropertiesResponse)
async def list_analytics_properties(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """List available GA4 accounts and properties."""
    google_settings = db.query(AdminGoogleSettings).filter(
        AdminGoogleSettings.admin_id == admin.id
    ).first()

    if not google_settings or not google_settings.access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google not connected"
        )

    service = GoogleAnalyticsService(access_token=google_settings.access_token)

    accounts = await service.list_accounts()
    properties = await service.list_properties()

    return GAPropertiesResponse(accounts=accounts, properties=properties)


@router.post("/analytics/select-property")
async def select_analytics_property(
    selection: GooglePropertySelect,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Select GA4 property to use."""
    google_settings = db.query(AdminGoogleSettings).filter(
        AdminGoogleSettings.admin_id == admin.id
    ).first()

    if not google_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google not connected"
        )

    if selection.property_id:
        google_settings.ga4_property_id = selection.property_id
    if selection.account_id:
        google_settings.ga4_account_id = selection.account_id

    google_settings.updated_at = datetime.now(UTC)
    db.commit()

    return {"message": "Property selected successfully"}


# ============================================================================
# GOOGLE BUSINESS PROFILE ENDPOINTS
# ============================================================================

async def get_business_service(
    db: Session,
    admin: AdminUser
) -> GoogleBusinessProfileService:
    """Get configured GMB service for admin."""
    google_settings = db.query(AdminGoogleSettings).filter(
        AdminGoogleSettings.admin_id == admin.id
    ).first()

    if not google_settings or not google_settings.access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google Business Profile not connected. Please connect your Google account."
        )

    if google_settings.token_expires_at and google_settings.token_expires_at < datetime.now(UTC):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google token expired. Please reconnect your Google account."
        )

    return GoogleBusinessProfileService(
        access_token=google_settings.access_token,
        account_id=google_settings.gmb_account_id,
        location_id=google_settings.gmb_location_id
    )


@router.get("/business/dashboard", response_model=GMBDashboardResponse)
async def get_business_dashboard(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get complete GMB dashboard data."""
    service = await get_business_service(db, admin)
    return await service.get_full_dashboard(days=days)


@router.get("/business/reviews", response_model=GMBReviewsResponse)
async def get_business_reviews(
    page_size: int = Query(20, ge=1, le=100),
    page_token: str | None = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get GMB reviews."""
    service = await get_business_service(db, admin)
    return await service.get_reviews(page_size=page_size, page_token=page_token)


@router.post("/business/reviews/{review_id}/reply")
async def reply_to_review(
    review_id: str,
    reply: GMBReviewReplyRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Reply to a GMB review."""
    service = await get_business_service(db, admin)
    success = await service.reply_to_review(review_id=review_id, reply_text=reply.reply_text)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to reply to review"
        )

    return {"message": "Reply posted successfully"}


@router.get("/business/posts", response_model=GMBPostsResponse)
async def get_business_posts(
    page_size: int = Query(20, ge=1, le=100),
    page_token: str | None = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get GMB posts."""
    service = await get_business_service(db, admin)
    return await service.get_posts(page_size=page_size, page_token=page_token)


@router.post("/business/posts")
async def create_business_post(
    post: GMBPostCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Create a new GMB post."""
    service = await get_business_service(db, admin)
    created_post = await service.create_post(post_data=post)

    if not created_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create post"
        )

    return created_post


@router.get("/business/insights")
async def get_business_insights(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get GMB insights."""
    service = await get_business_service(db, admin)
    return await service.get_insights(days=days)


@router.get("/business/locations", response_model=GMBLocationsResponse)
async def list_business_locations(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """List available GMB accounts and locations."""
    google_settings = db.query(AdminGoogleSettings).filter(
        AdminGoogleSettings.admin_id == admin.id
    ).first()

    if not google_settings or not google_settings.access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google not connected"
        )

    service = GoogleBusinessProfileService(access_token=google_settings.access_token)

    accounts = await service.list_accounts()

    # Get locations for first account if available
    locations = []
    if accounts:
        first_account = accounts[0].get("name", "")
        locations = await service.list_locations(account_id=first_account)

    return GMBLocationsResponse(accounts=accounts, locations=locations)


@router.post("/business/select-location")
async def select_business_location(
    selection: GooglePropertySelect,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Select GMB location to use."""
    google_settings = db.query(AdminGoogleSettings).filter(
        AdminGoogleSettings.admin_id == admin.id
    ).first()

    if not google_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Google not connected"
        )

    if selection.account_id:
        google_settings.gmb_account_id = selection.account_id
    if selection.location_id:
        google_settings.gmb_location_id = selection.location_id

    google_settings.updated_at = datetime.now(UTC)
    db.commit()

    return {"message": "Location selected successfully"}


# ============================================================================
# GOOGLE CALENDAR + MEET ENDPOINTS
# ============================================================================

from .calendar_service import (
    GoogleCalendarService,
    cancel_booking_event,
    create_booking_with_meet,
    get_available_slots,
)


class CalendarEventCreate(BaseModel):
    """Create calendar event with Meet."""
    title: str
    description: str = ""
    start_time: datetime
    duration_minutes: int = 60
    attendee_email: str
    attendee_name: str = ""


class CalendarEventResponse(BaseModel):
    """Calendar event response."""
    event_id: str | None = None
    html_link: str | None = None
    meet_link: str | None = None
    meet_id: str | None = None
    status: str | None = None


class AvailableSlotsRequest(BaseModel):
    """Request for available slots."""
    date: datetime
    duration_minutes: int = 60


@router.get("/calendar/status")
async def get_calendar_status(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Check if Google Calendar is connected (via main Google token)."""
    google_settings = db.query(AdminGoogleSettings).filter(
        AdminGoogleSettings.admin_id == admin.id
    ).first()

    if not google_settings or not google_settings.access_token:
        return {"connected": False, "expires_at": None}

    # Check if calendar scopes are present in main token
    scopes = google_settings.scopes or ""
    has_calendar = "calendar" in scopes.lower()

    return {
        "connected": has_calendar,
        "expires_at": google_settings.token_expires_at
    }


@router.post("/calendar/events", response_model=CalendarEventResponse)
async def create_calendar_event_with_meet(
    event: CalendarEventCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Create a calendar event with Google Meet link."""
    result = await create_booking_with_meet(
        db=db,
        admin_id=admin.id,
        booking_title=event.title,
        booking_description=event.description,
        start_time=event.start_time,
        duration_minutes=event.duration_minutes,
        client_email=event.attendee_email,
        client_name=event.attendee_name
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create calendar event. Check Google connection."
        )

    return CalendarEventResponse(**result)


@router.get("/calendar/events")
async def list_calendar_events(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """List upcoming calendar events."""
    service = GoogleCalendarService.from_admin_token(db, admin.id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google Calendar not connected"
        )

    events = await service.list_events(
        time_max=datetime.now(UTC) + timedelta(days=days)
    )

    return {"events": events, "count": len(events)}


@router.delete("/calendar/events/{event_id}")
async def delete_calendar_event(
    event_id: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Delete a calendar event."""
    success = await cancel_booking_event(db, admin.id, event_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete event"
        )

    return {"message": "Event deleted successfully"}


@router.post("/calendar/available-slots")
async def get_calendar_available_slots(
    request: AvailableSlotsRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get available time slots for a specific date."""
    slots = await get_available_slots(
        db=db,
        admin_id=admin.id,
        date=request.date,
        duration_minutes=request.duration_minutes
    )

    return {"date": request.date.date().isoformat(), "slots": slots}


@router.get("/calendar/calendars")
async def list_calendars(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """List all calendars accessible to the user."""
    service = GoogleCalendarService.from_admin_token(db, admin.id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google Calendar not connected"
        )

    calendars = await service.list_calendars()
    return {"calendars": calendars}


# ============================================================================
# GMAIL EMAIL ENDPOINTS
# ============================================================================

from .gmail_service import GmailService, send_booking_confirmation, send_quote_email


class SendEmailRequest(BaseModel):
    """Send email request."""
    to: str
    subject: str
    body_html: str
    body_text: str | None = None
    reply_to: str | None = None


class BookingEmailRequest(BaseModel):
    """Booking confirmation email request."""
    client_email: str
    client_name: str
    booking_title: str
    booking_date: datetime
    duration_minutes: int = 60
    meet_link: str | None = None
    calendar_link: str | None = None


class QuoteEmailRequest(BaseModel):
    """Quote email request."""
    client_email: str
    client_name: str
    project_title: str
    total_amount: float
    valid_until: datetime
    quote_pdf_link: str


@router.get("/gmail/status")
async def get_gmail_status(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Check if Gmail is connected."""
    google_settings = db.query(AdminGoogleSettings).filter(
        AdminGoogleSettings.admin_id == admin.id
    ).first()

    if not google_settings or not google_settings.access_token:
        return {"connected": False}

    scopes = google_settings.scopes or ""
    has_gmail = "gmail" in scopes.lower() or "mail" in scopes.lower()

    return {"connected": has_gmail}


@router.post("/gmail/send")
async def send_email(
    request: SendEmailRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Send a custom email via Gmail."""
    service = GmailService.from_admin_token(db, admin.id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Gmail not connected"
        )

    result = await service.send_email(
        to=request.to,
        subject=request.subject,
        body_html=request.body_html,
        body_text=request.body_text,
        reply_to=request.reply_to
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )

    return {"message": "Email sent successfully", "message_id": result.get("id")}


@router.post("/gmail/send-booking-confirmation")
async def send_booking_confirmation_email(
    request: BookingEmailRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Send booking confirmation email."""
    success = await send_booking_confirmation(
        db=db,
        admin_id=admin.id,
        client_email=request.client_email,
        client_name=request.client_name,
        booking_title=request.booking_title,
        booking_date=request.booking_date,
        duration_minutes=request.duration_minutes,
        meet_link=request.meet_link,
        calendar_link=request.calendar_link
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send confirmation email"
        )

    return {"message": "Confirmation email sent successfully"}


@router.post("/gmail/send-quote")
async def send_quote_email_endpoint(
    request: QuoteEmailRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Send quote/preventivo email."""
    success = await send_quote_email(
        db=db,
        admin_id=admin.id,
        client_email=request.client_email,
        client_name=request.client_name,
        project_title=request.project_title,
        total_amount=request.total_amount,
        valid_until=request.valid_until,
        quote_pdf_link=request.quote_pdf_link
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send quote email"
        )

    return {"message": "Quote email sent successfully"}


# ============================================================================
# GOOGLE DOCS - QUOTES/PREVENTIVI
# ============================================================================

from .docs_service import GoogleDocsService, generate_quote_pdf, get_or_create_quotes_folder


class QuoteGenerateRequest(BaseModel):
    """Generate quote from template."""
    template_id: str | None = None
    quote_number: str | None = None
    client_name: str
    client_email: str
    client_company: str = ""
    client_address: str = ""
    project_title: str
    project_description: str = ""
    items: list[dict] = []  # [{description, quantity, unit_price, total}]
    subtotal: float = 0
    vat_rate: float = 22
    vat_amount: float = 0
    total: float = 0
    valid_days: int = 30
    notes: str = ""


@router.get("/docs/status")
async def get_docs_status(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Check if Google Docs/Drive is connected."""
    google_settings = db.query(AdminGoogleSettings).filter(
        AdminGoogleSettings.admin_id == admin.id
    ).first()

    if not google_settings or not google_settings.access_token:
        return {"connected": False}

    scopes = google_settings.scopes or ""
    has_drive = "drive" in scopes.lower()

    return {"connected": has_drive}


@router.post("/docs/generate-quote")
async def generate_quote(
    request: QuoteGenerateRequest,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Generate a quote PDF from template."""
    # Get or create quotes folder
    folder_id = await get_or_create_quotes_folder(db, admin.id)

    # Use default template if not provided
    template_id = request.template_id or settings.GOOGLE_QUOTE_TEMPLATE_ID if hasattr(settings, "GOOGLE_QUOTE_TEMPLATE_ID") else None

    if not template_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No quote template configured. Set GOOGLE_QUOTE_TEMPLATE_ID in settings."
        )

    quote_data = {
        "quote_number": request.quote_number,
        "client_name": request.client_name,
        "client_email": request.client_email,
        "client_company": request.client_company,
        "client_address": request.client_address,
        "project_title": request.project_title,
        "project_description": request.project_description,
        "items": request.items,
        "subtotal": request.subtotal,
        "vat_rate": request.vat_rate,
        "vat_amount": request.vat_amount,
        "total": request.total,
        "valid_until": datetime.now() + timedelta(days=request.valid_days),
        "notes": request.notes
    }

    result = await generate_quote_pdf(
        db=db,
        admin_id=admin.id,
        template_id=template_id,
        quote_data=quote_data,
        output_folder_id=folder_id
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate quote"
        )

    return result


@router.get("/docs/templates")
async def list_doc_templates(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """List available document templates."""
    service = GoogleDocsService.from_admin_token(db, admin.id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google Drive not connected"
        )

    # List Google Docs files (templates)
    docs = await service.list_files(
        mime_type="application/vnd.google-apps.document"
    )

    return {"templates": docs}


@router.get("/docs/quotes")
async def list_generated_quotes(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """List generated quotes."""
    service = GoogleDocsService.from_admin_token(db, admin.id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google Drive not connected"
        )

    folder_id = await get_or_create_quotes_folder(db, admin.id)
    if not folder_id:
        return {"quotes": []}

    # List PDFs in quotes folder
    pdfs = await service.list_files(
        folder_id=folder_id,
        mime_type="application/pdf"
    )

    return {"quotes": pdfs, "folder_id": folder_id}


# ============================================================================
# GOOGLE SEARCH CONSOLE - SEO ANALYTICS
# ============================================================================

from .search_console_service import GoogleSearchConsoleService


async def get_search_console_service(
    db: Session,
    admin: AdminUser
) -> GoogleSearchConsoleService:
    """Get configured Search Console service for admin."""
    service = GoogleSearchConsoleService.from_admin_token(db, admin.id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google Search Console not connected. Please connect your Google account with Search Console access."
        )
    return service


@router.get("/search-console/status")
async def get_search_console_status(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Check if Search Console is connected."""
    google_settings = db.query(AdminGoogleSettings).filter(
        AdminGoogleSettings.admin_id == admin.id
    ).first()

    if not google_settings or not google_settings.access_token:
        return {"connected": False}

    scopes = google_settings.scopes or ""
    has_gsc = "webmasters" in scopes.lower()

    return {"connected": has_gsc, "site_url": "https://markettina.com"}


@router.get("/search-console/sites")
async def list_search_console_sites(
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """List all verified sites in Search Console."""
    service = await get_search_console_service(db, admin)
    sites = await service.list_sites()
    return {"sites": sites}


@router.get("/search-console/dashboard")
async def get_search_console_dashboard(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get complete SEO dashboard from Search Console."""
    # Check connection first
    google_settings = db.query(AdminGoogleSettings).filter(
        AdminGoogleSettings.admin_id == admin.id
    ).first()

    if not google_settings or not google_settings.access_token:
        return {
            "connected": False,
            "message": "Google Search Console non connesso. Vai su Settings → Integrations per connettere Google.",
            "overview": None,
            "top_queries": [],
            "top_pages": [],
            "daily_data": [],
            "devices": [],
            "countries": [],
            "toolai_performance": None,
            "keyword_opportunities": []
        }

    scopes = google_settings.scopes or ""
    if "webmasters" not in scopes.lower():
        return {
            "connected": False,
            "message": "Scope Search Console mancante. Disconnetti e riconnetti Google per autorizzare Search Console.",
            "overview": None,
            "top_queries": [],
            "top_pages": [],
            "daily_data": [],
            "devices": [],
            "countries": [],
            "toolai_performance": None,
            "keyword_opportunities": []
        }

    try:
        service = GoogleSearchConsoleService.from_admin_token(db, admin.id)
        if not service:
            raise ValueError("Service initialization failed")
        dashboard = service.get_full_seo_dashboard(days)
        dashboard["connected"] = True
        return dashboard
    except Exception as e:
        logger.error(f"Error fetching Search Console dashboard: {e}")
        return {
            "connected": False,
            "message": f"Errore nel recupero dati: {e!s}",
            "overview": None,
            "top_queries": [],
            "top_pages": [],
            "daily_data": [],
            "devices": [],
            "countries": [],
            "toolai_performance": None,
            "keyword_opportunities": []
        }


@router.get("/search-console/overview")
async def get_search_console_overview(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get SEO overview metrics."""
    service = await get_search_console_service(db, admin)
    overview = await service.get_overview_metrics(days)
    return overview


@router.get("/search-console/queries")
async def get_search_console_queries(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get top performing search queries."""
    service = await get_search_console_service(db, admin)
    queries = await service.get_top_queries(days, limit)
    return {"queries": queries, "count": len(queries)}


@router.get("/search-console/pages")
async def get_search_console_pages(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get top performing pages."""
    service = await get_search_console_service(db, admin)
    pages = await service.get_top_pages(days, limit)
    return {"pages": pages, "count": len(pages)}


@router.get("/search-console/devices")
async def get_search_console_devices(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get performance by device type."""
    service = await get_search_console_service(db, admin)
    devices = await service.get_device_breakdown(days)
    return {"devices": devices}


@router.get("/search-console/countries")
async def get_search_console_countries(
    days: int = Query(30, ge=1, le=365),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get performance by country."""
    service = await get_search_console_service(db, admin)
    countries = await service.get_country_breakdown(days, limit)
    return {"countries": countries, "count": len(countries)}


@router.get("/search-console/daily")
async def get_search_console_daily(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get daily performance metrics for charts."""
    service = await get_search_console_service(db, admin)
    daily = await service.get_daily_performance(days)
    return {"daily": daily, "count": len(daily)}


@router.get("/search-console/toolai")
async def get_search_console_toolai(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get performance specifically for ToolAI pages."""
    service = await get_search_console_service(db, admin)
    toolai = await service.get_toolai_performance(days)
    return toolai


@router.get("/search-console/opportunities")
async def get_keyword_opportunities(
    days: int = Query(30, ge=1, le=365),
    min_impressions: int = Query(100, ge=10, le=10000),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get keyword optimization opportunities (high impressions, low CTR)."""
    service = await get_search_console_service(db, admin)
    opportunities = await service.get_keyword_opportunities(days, min_impressions)
    return {"opportunities": opportunities, "count": len(opportunities)}


# ============================================================================
# GOOGLE TRENDS - MARKETING INSIGHTS
# ============================================================================

from .trends_service import GoogleTrendsService, get_marketing_insights, suggest_content_topics


class TrendsKeywordsRequest(BaseModel):
    """Trends analysis request."""
    keywords: list[str] = []
    industry: str = "technology"


@router.get("/trends/daily")
async def get_daily_trends(
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get daily trending searches in Italy."""
    service = GoogleTrendsService(geo="IT", hl="it")
    trends = await service.get_daily_trends()
    return {"trends": trends, "region": "IT"}


@router.get("/trends/realtime")
async def get_realtime_trends(
    category: str = Query("business", regex="^(all|business|entertainment|health|science|sports|top)$"),
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get real-time trending stories."""
    service = GoogleTrendsService(geo="IT", hl="it")
    stories = await service.get_realtime_trends(category=category)
    return {"stories": stories, "category": category}


@router.post("/trends/insights")
async def get_trends_insights(
    request: TrendsKeywordsRequest,
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get comprehensive marketing insights from trends."""
    insights = await get_marketing_insights(
        keywords=request.keywords if request.keywords else None,
        industry=request.industry
    )
    return insights


@router.post("/trends/content-suggestions")
async def get_content_suggestions(
    request: TrendsKeywordsRequest,
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get content topic suggestions based on trends."""
    services = request.keywords if request.keywords else None
    suggestions = await suggest_content_topics(
        business_type="web_agency",
        current_services=services
    )
    return {"suggestions": suggestions}


@router.get("/trends/related/{keyword}")
async def get_related_queries(
    keyword: str,
    admin: AdminUser = Depends(get_current_admin_user)
):
    """Get related queries for a keyword."""
    service = GoogleTrendsService()
    related = await service.get_related_queries(keyword)
    return {"keyword": keyword, **related}
