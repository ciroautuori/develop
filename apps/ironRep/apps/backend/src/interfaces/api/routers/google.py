"""
Google Integration API Router - Calendar, YouTube & Fit
"""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import uuid

from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.models import GoogleAccountModel, BiometricEntryModel
from src.infrastructure.security.security import CurrentUser
from src.infrastructure.external.google_oauth_service import google_oauth_service, get_all_scopes
from src.infrastructure.external.google_calendar_service import GoogleCalendarService
from src.infrastructure.external.google_fit_service import GoogleFitService
from src.infrastructure.external.youtube_service import youtube_service
from src.infrastructure.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


class AuthUrlResponse(BaseModel):
    authorization_url: str

class TokenExchangeRequest(BaseModel):
    code: str
    state: Optional[str] = None

class TokenExchangeResponse(BaseModel):
    success: bool
    google_email: Optional[str] = None
    scopes: List[str] = []

class ConnectionStatusResponse(BaseModel):
    connected: bool
    google_email: Optional[str] = None
    scopes: List[str] = []
    fit_sync_enabled: bool = False
    calendar_sync_enabled: bool = False
    last_fit_sync_at: Optional[str] = None

class CalendarEventRequest(BaseModel):
    title: str
    description: str
    start_time: datetime
    duration_minutes: int = 60
    exercises: Optional[List[str]] = None

class CalendarEventResponse(BaseModel):
    event_id: str
    html_link: str
    summary: str

class FitSyncResponse(BaseModel):
    success: bool
    weight: List[dict] = []
    steps: List[dict] = []
    heart_rate: List[dict] = []
    calories_today: int = 0
    synced_at: str

class YouTubeSearchResponse(BaseModel):
    videos: List[dict]


@router.get("/auth/url", response_model=AuthUrlResponse)
async def get_authorization_url(current_user: CurrentUser):
    """Get Google OAuth2 authorization URL."""
    try:
        url = google_oauth_service.get_authorization_url(scopes=get_all_scopes(), state=current_user.id)
        return AuthUrlResponse(authorization_url=url)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))


@router.get("/auth/callback", response_class=HTMLResponse)
async def oauth_callback_page(code: Optional[str] = Query(None), state: Optional[str] = Query(None), error: Optional[str] = Query(None)):
    if error:
        safe_error = str(error).replace("<", "").replace(">", "")
        return HTMLResponse(
            f"""<!doctype html>
<html><head><meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
<title>Google OAuth</title></head>
<body style=\"font-family:system-ui;padding:24px;\">
  <h3>Autorizzazione Google non completata</h3>
  <p>Errore: <code>{safe_error}</code></p>
  <p>Puoi chiudere questa finestra e riprovare.</p>
</body></html>""",
            status_code=400,
        )

    if not code:
        return HTMLResponse(
            """<!doctype html>
<html><head><meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
<title>Google OAuth</title></head>
<body style=\"font-family:system-ui;padding:24px;\">
  <h3>Callback Google</h3>
  <p>Parametro <code>code</code> mancante.</p>
</body></html>""",
            status_code=400,
        )

    safe_code = str(code).replace("<", "").replace(">", "")
    safe_state = (str(state) if state is not None else "").replace("<", "").replace(">", "")
    return HTMLResponse(
        f"""<!doctype html>
<html><head><meta charset=\"utf-8\" /><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
<title>Google OAuth</title></head>
<body style=\"font-family:system-ui;padding:24px;\">
  <h3>Connessione completata</h3>
  <p>Puoi chiudere questa finestra.</p>
  <script>
    (function () {{
      try {{
        if (window.opener) {{
          window.opener.postMessage({{ type: 'google-oauth-callback', code: '{safe_code}', state: '{safe_state}' }}, '*');
          try {{ window.close(); }} catch (e) {{}}
          return;
        }}

        var target = '/login?google_code=' + encodeURIComponent('{safe_code}') + '&state=' + encodeURIComponent('{safe_state}');
        window.location.replace(target);
      }} catch (e) {{}}
    }})();
  </script>
</body></html>""",
        status_code=200,
    )


@router.post("/auth/callback", response_model=TokenExchangeResponse)
async def exchange_authorization_code(request: TokenExchangeRequest, current_user: CurrentUser, db: Session = Depends(get_db)):
    """Exchange authorization code for tokens."""
    try:
        tokens = google_oauth_service.exchange_code_for_tokens(request.code)
        creds = google_oauth_service.get_credentials(tokens["access_token"], tokens["refresh_token"],
                                                     datetime.fromisoformat(tokens["expires_at"]) if tokens["expires_at"] else None)
        user_info = google_oauth_service.get_user_info(creds)

        existing = db.query(GoogleAccountModel).filter(GoogleAccountModel.google_user_id == user_info["google_user_id"]).first()
        if existing and existing.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account già collegato ad altro utente.")

        google_account = db.query(GoogleAccountModel).filter(GoogleAccountModel.user_id == current_user.id).first()
        if google_account:
            google_account.access_token = tokens["access_token"]
            google_account.refresh_token = tokens["refresh_token"] or google_account.refresh_token
            google_account.token_expires_at = datetime.fromisoformat(tokens["expires_at"]) if tokens["expires_at"] else None
            google_account.scopes = tokens["scopes"]
            google_account.google_user_id = user_info["google_user_id"]
            google_account.google_email = user_info["email"]
            google_account.updated_at = datetime.now()
        else:
            google_account = GoogleAccountModel(
                id=str(uuid.uuid4()), user_id=current_user.id, access_token=tokens["access_token"],
                refresh_token=tokens["refresh_token"],
                token_expires_at=datetime.fromisoformat(tokens["expires_at"]) if tokens["expires_at"] else None,
                scopes=tokens["scopes"], google_user_id=user_info["google_user_id"], google_email=user_info["email"],
                fit_sync_enabled=True, calendar_sync_enabled=True, created_at=datetime.now(), updated_at=datetime.now(),
            )
            db.add(google_account)
        db.commit()
        logger.info(f"Google linked for user {current_user.id}: {user_info['email']}")
        return TokenExchangeResponse(success=True, google_email=user_info["email"], scopes=tokens["scopes"])
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token exchange failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Errore autorizzazione: {str(e)}")


@router.get("/auth/status", response_model=ConnectionStatusResponse)
async def get_connection_status(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Check Google account connection status."""
    account = db.query(GoogleAccountModel).filter(GoogleAccountModel.user_id == current_user.id).first()
    if not account:
        return ConnectionStatusResponse(connected=False)
    return ConnectionStatusResponse(
        connected=True, google_email=account.google_email, scopes=account.scopes or [],
        fit_sync_enabled=account.fit_sync_enabled, calendar_sync_enabled=account.calendar_sync_enabled,
        last_fit_sync_at=account.last_fit_sync_at.isoformat() if account.last_fit_sync_at else None,
    )


@router.delete("/auth/disconnect")
async def disconnect_google_account(current_user: CurrentUser, db: Session = Depends(get_db)):
    """Disconnect Google account."""
    account = db.query(GoogleAccountModel).filter(GoogleAccountModel.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Nessun account Google collegato.")
    google_oauth_service.revoke_token(account.access_token)
    db.delete(account)
    db.commit()
    return {"success": True, "message": "Account Google disconnesso."}


def _get_credentials(account: GoogleAccountModel):
    if account.token_expires_at and account.token_expires_at < datetime.now():
        new = google_oauth_service.refresh_access_token(account.refresh_token)
        account.access_token = new["access_token"]
        account.token_expires_at = datetime.fromisoformat(new["expires_at"]) if new["expires_at"] else None
    return google_oauth_service.get_credentials(account.access_token, account.refresh_token, account.token_expires_at)


# ==================== FIT ENDPOINTS ====================

@router.post("/fit/sync", response_model=FitSyncResponse)
async def sync_google_fit_data(current_user: CurrentUser, days: int = Query(7, ge=1, le=30), db: Session = Depends(get_db)):
    """Sync biometric data from Google Fit."""
    account = db.query(GoogleAccountModel).filter(GoogleAccountModel.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account Google non collegato.")
    if not account.fit_sync_enabled:
        raise HTTPException(status_code=403, detail="Sincronizzazione Fit disabilitata.")

    try:
        fit_service = GoogleFitService(_get_credentials(account))
        data = fit_service.sync_all_biometrics(days)

        # Save weight entries to biometrics
        for w in data.get("weight", []):
            existing = db.query(BiometricEntryModel).filter(
                BiometricEntryModel.user_id == current_user.id,
                BiometricEntryModel.type == "BODY_COMP",
                BiometricEntryModel.date == datetime.fromisoformat(w["date"]),
            ).first()
            if not existing:
                db.add(BiometricEntryModel(
                    id=str(uuid.uuid4()), user_id=current_user.id,
                    date=datetime.fromisoformat(w["date"]), type="BODY_COMP",
                    weight=w["weight_kg"], notes="Google Fit", created_at=datetime.now(),
                ))

        account.last_fit_sync_at = datetime.now()
        db.commit()
        logger.info(f"Fit sync completed for user {current_user.id}")

        return FitSyncResponse(success=True, weight=data.get("weight", []), steps=data.get("steps", []),
                              heart_rate=data.get("heart_rate", []), calories_today=data.get("calories_today", 0),
                              synced_at=data.get("synced_at", datetime.now().isoformat()))
    except Exception as e:
        logger.error(f"Fit sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Errore sync: {str(e)}")


@router.get("/fit/weight")
async def get_fit_weight_history(current_user: CurrentUser, days: int = Query(30, ge=1, le=90), db: Session = Depends(get_db)):
    """Get weight history from Google Fit."""
    account = db.query(GoogleAccountModel).filter(GoogleAccountModel.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account Google non collegato.")
    return {"weight": GoogleFitService(_get_credentials(account)).get_weight_history(days)}


@router.get("/fit/steps")
async def get_fit_steps_history(current_user: CurrentUser, days: int = Query(7, ge=1, le=30), db: Session = Depends(get_db)):
    """Get daily steps from Google Fit."""
    account = db.query(GoogleAccountModel).filter(GoogleAccountModel.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account Google non collegato.")
    return {"steps": GoogleFitService(_get_credentials(account)).get_steps_history(days)}


# ==================== CALENDAR ENDPOINTS ====================

@router.post("/calendar/events", response_model=CalendarEventResponse)
async def create_calendar_event(request: CalendarEventRequest, current_user: CurrentUser, db: Session = Depends(get_db)):
    """Create a workout event in Google Calendar."""
    account = db.query(GoogleAccountModel).filter(GoogleAccountModel.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account Google non collegato.")
    try:
        svc = GoogleCalendarService(_get_credentials(account))
        event = svc.create_workout_event(request.title, request.description, request.start_time, request.duration_minutes, request.exercises)
        db.commit()
        return CalendarEventResponse(event_id=event["event_id"], html_link=event["html_link"], summary=event["summary"])
    except Exception as e:
        logger.error(f"Calendar event failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/calendar/events")
async def list_calendar_events(current_user: CurrentUser, days: int = Query(7, ge=1, le=30), db: Session = Depends(get_db)):
    """List upcoming calendar events."""
    account = db.query(GoogleAccountModel).filter(GoogleAccountModel.user_id == current_user.id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account Google non collegato.")
    return {"events": GoogleCalendarService(_get_credentials(account)).list_upcoming_events(days)}


# ==================== YOUTUBE ENDPOINTS ====================

@router.get("/youtube/search", response_model=YouTubeSearchResponse)
async def search_youtube_videos(query: str = Query(..., min_length=2), max_results: int = Query(5, ge=1, le=10)):
    """Search exercise tutorial videos on YouTube."""
    return YouTubeSearchResponse(videos=youtube_service.search_exercise_videos(query, max_results=max_results))


@router.get("/youtube/video/{video_id}")
async def get_youtube_video_details(video_id: str):
    """Get video details."""
    details = youtube_service.get_video_details(video_id)
    if not details:
        raise HTTPException(status_code=404, detail="Video non trovato.")
    return details
