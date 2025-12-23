"""
Zoom Integration - OAuth2 + Meeting API
"""

import base64
import os
from datetime import datetime
from typing import Any

import aiohttp


class ZoomIntegration:
    """Zoom integration using OAuth and Meeting API"""

    def __init__(self):
        self.client_id = os.getenv("ZOOM_CLIENT_ID")
        self.client_secret = os.getenv("ZOOM_CLIENT_SECRET")
        self.redirect_uri = os.getenv("ZOOM_REDIRECT_URI", "http://localhost:8000/api/v1/integrations/zoom/callback")
        self.api_base = "https://api.zoom.us/v2"

        if not self.client_id or not self.client_secret:
            raise ValueError("Zoom OAuth credentials not configured")

    def get_authorization_url(self, state: str) -> str:
        """Get OAuth authorization URL"""
        return (
            f"https://zoom.us/oauth/authorize"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&state={state}"
        )

    async def exchange_code_for_tokens(self, code: str) -> dict[str, Any]:
        """Exchange authorization code for tokens"""
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        async with aiohttp.ClientSession() as session, session.post(
            "https://zoom.us/oauth/token",
            headers={"Authorization": f"Basic {auth_header}"},
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
            }
        ) as response:
            if response.status != 200:
                raise Exception(f"Zoom OAuth error: {await response.text()}")

            data = await response.json()
            return {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_in": data["expires_in"],
                "scope": data["scope"],
            }

    async def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh access token using refresh token"""
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        async with aiohttp.ClientSession() as session, session.post(
            "https://zoom.us/oauth/token",
            headers={"Authorization": f"Basic {auth_header}"},
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }
        ) as response:
            if response.status != 200:
                raise Exception(f"Zoom token refresh error: {await response.text()}")

            data = await response.json()
            return {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "expires_in": data["expires_in"],
            }

    async def create_meeting(
        self,
        access_token: str,
        title: str,
        description: str,
        start_time: datetime,
        duration_minutes: int,
        timezone: str = "Europe/Rome",
        password: str | None = None
    ) -> dict[str, Any]:
        """Create Zoom meeting"""

        meeting_data = {
            "topic": title,
            "type": 2,  # Scheduled meeting
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            "duration": duration_minutes,
            "timezone": timezone,
            "agenda": description,
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "mute_upon_entry": True,
                "watermark": False,
                "use_pmi": False,
                "approval_type": 2,  # No registration required
                "audio": "both",
                "auto_recording": "none",
                "waiting_room": True,
            }
        }

        if password:
            meeting_data["password"] = password

        async with aiohttp.ClientSession() as session, session.post(
            f"{self.api_base}/users/me/meetings",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json=meeting_data
        ) as response:
            if response.status != 201:
                raise Exception(f"Zoom API error: {await response.text()}")

            data = await response.json()
            return {
                "meeting_id": str(data["id"]),
                "meeting_url": data["join_url"],
                "meeting_password": data.get("password"),
                "start_url": data["start_url"],
                "status": "created",
            }

    async def cancel_meeting(self, access_token: str, meeting_id: str) -> bool:
        """Cancel Zoom meeting"""
        async with aiohttp.ClientSession() as session, session.delete(
            f"{self.api_base}/meetings/{meeting_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        ) as response:
            return response.status == 204

    async def update_meeting(
        self,
        access_token: str,
        meeting_id: str,
        start_time: datetime | None = None,
        duration_minutes: int | None = None,
        timezone: str = "Europe/Rome"
    ) -> dict[str, Any]:
        """Update Zoom meeting"""

        update_data = {}
        if start_time:
            update_data["start_time"] = start_time.strftime("%Y-%m-%dT%H:%M:%S")
            update_data["timezone"] = timezone
        if duration_minutes:
            update_data["duration"] = duration_minutes

        async with aiohttp.ClientSession() as session, session.patch(
            f"{self.api_base}/meetings/{meeting_id}",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            json=update_data
        ) as response:
            if response.status != 204:
                raise Exception(f"Zoom API error: {await response.text()}")

            return {"meeting_id": meeting_id, "status": "updated"}

    async def get_meeting(self, access_token: str, meeting_id: str) -> dict[str, Any]:
        """Get Zoom meeting details"""
        async with aiohttp.ClientSession() as session, session.get(
            f"{self.api_base}/meetings/{meeting_id}",
            headers={"Authorization": f"Bearer {access_token}"}
        ) as response:
            if response.status != 200:
                raise Exception(f"Zoom API error: {await response.text()}")

            return await response.json()


# Singleton instance
zoom = ZoomIntegration()
