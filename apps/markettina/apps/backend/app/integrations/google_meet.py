"""
Google Meet Integration - OAuth2 + Calendar API
"""

import os
from datetime import datetime, timedelta
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleMeetIntegration:
    """Google Meet integration using Calendar API"""

    SCOPES = [
        "https://www.googleapis.com/auth/calendar.events",
    ]

    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/v1/integrations/google/callback")

        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth credentials not configured")

    def get_authorization_url(self, state: str) -> str:
        """Get OAuth authorization URL"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri,
        )

        authorization_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            state=state,
            prompt="consent"
        )

        return authorization_url

    def exchange_code_for_tokens(self, code: str) -> dict[str, Any]:
        """Exchange authorization code for tokens"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri],
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri,
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
        }

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh access token using refresh token"""
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        credentials.refresh(Request())

        return {
            "access_token": credentials.token,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
        }

    async def create_meeting(
        self,
        access_token: str,
        title: str,
        description: str,
        start_time: datetime,
        duration_minutes: int,
        attendees: list[str],
        timezone: str = "Europe/Rome"
    ) -> dict[str, Any]:
        """Create Google Meet meeting via Calendar API"""

        credentials = Credentials(token=access_token)
        service = build("calendar", "v3", credentials=credentials)

        end_time = start_time + timedelta(minutes=duration_minutes)

        event = {
            "summary": title,
            "description": description,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": timezone,
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": timezone,
            },
            "attendees": [{"email": email} for email in attendees],
            "conferenceData": {
                "createRequest": {
                    "requestId": f"meet-{int(start_time.timestamp())}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 24 * 60},
                    {"method": "popup", "minutes": 30},
                ],
            },
        }

        try:
            event = service.events().insert(
                calendarId="primary",
                body=event,
                conferenceDataVersion=1,
                sendUpdates="all"
            ).execute()

            # Extract Google Meet link
            meet_link = None
            if "conferenceData" in event and "entryPoints" in event["conferenceData"]:
                for entry in event["conferenceData"]["entryPoints"]:
                    if entry["entryPointType"] == "video":
                        meet_link = entry["uri"]
                        break

            return {
                "event_id": event["id"],
                "meeting_url": meet_link,
                "html_link": event.get("htmlLink"),
                "status": event.get("status"),
            }

        except HttpError as error:
            raise Exception(f"Google Calendar API error: {error}")

    async def cancel_meeting(self, access_token: str, event_id: str) -> bool:
        """Cancel Google Meet meeting"""
        credentials = Credentials(token=access_token)
        service = build("calendar", "v3", credentials=credentials)

        try:
            service.events().delete(
                calendarId="primary",
                eventId=event_id,
                sendUpdates="all"
            ).execute()
            return True
        except HttpError as error:
            raise Exception(f"Google Calendar API error: {error}")

    async def update_meeting(
        self,
        access_token: str,
        event_id: str,
        start_time: datetime | None = None,
        duration_minutes: int | None = None,
        timezone: str = "Europe/Rome"
    ) -> dict[str, Any]:
        """Update Google Meet meeting"""
        credentials = Credentials(token=access_token)
        service = build("calendar", "v3", credentials=credentials)

        try:
            # Get existing event
            event = service.events().get(
                calendarId="primary",
                eventId=event_id
            ).execute()

            # Update fields
            if start_time:
                end_time = start_time + timedelta(minutes=duration_minutes or 30)
                event["start"] = {
                    "dateTime": start_time.isoformat(),
                    "timeZone": timezone,
                }
                event["end"] = {
                    "dateTime": end_time.isoformat(),
                    "timeZone": timezone,
                }

            # Update event
            updated_event = service.events().update(
                calendarId="primary",
                eventId=event_id,
                body=event,
                sendUpdates="all"
            ).execute()

            return {
                "event_id": updated_event["id"],
                "status": updated_event.get("status"),
            }

        except HttpError as error:
            raise Exception(f"Google Calendar API error: {error}")


# Singleton instance
google_meet = GoogleMeetIntegration()
