"""
🔗 LinkedIn API Publishing Service

Pubblicazione REALE su LinkedIn via API ufficiale.

Features:
- OAuth 2.0 con LinkedIn
- Post testuali
- Post con immagini
- Post con video
- Articoli (long-form)
- Company page posting
- Analytics base

API Docs: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/posts-api
"""

import os
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import httpx
import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger(__name__)


# =============================================================================
# MODELS
# =============================================================================

class LinkedInVisibility(str, Enum):
    """Visibilità del post."""
    ANYONE = "PUBLIC"          # Visibile a tutti
    CONNECTIONS = "CONNECTIONS"  # Solo connessioni
    LOGGED_IN = "LOGGED_IN"    # Solo utenti LinkedIn


class LinkedInMediaType(str, Enum):
    """Tipo di media."""
    NONE = "NONE"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    ARTICLE = "ARTICLE"
    DOCUMENT = "DOCUMENT"


class LinkedInPostRequest(BaseModel):
    """Request per creare un post LinkedIn."""
    text: str
    visibility: LinkedInVisibility = LinkedInVisibility.ANYONE
    media_type: LinkedInMediaType = LinkedInMediaType.NONE
    media_url: Optional[str] = None
    media_title: Optional[str] = None
    media_description: Optional[str] = None
    article_url: Optional[str] = None

    # For company pages
    is_company_post: bool = False
    company_id: Optional[str] = None


class LinkedInPostResponse(BaseModel):
    """Response dopo pubblicazione."""
    success: bool
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error: Optional[str] = None


class LinkedInProfile(BaseModel):
    """Profilo LinkedIn."""
    id: str
    first_name: str
    last_name: str
    profile_url: Optional[str] = None
    profile_picture_url: Optional[str] = None
    headline: Optional[str] = None


class LinkedInCompanyPage(BaseModel):
    """Company page LinkedIn."""
    id: str
    name: str
    vanity_name: Optional[str] = None
    logo_url: Optional[str] = None


class LinkedInAuthConfig(BaseModel):
    """Configurazione OAuth LinkedIn."""
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: list[str] = Field(default_factory=lambda: [
        "openid",
        "profile",
        "email",
        "w_member_social",  # Post as member
    ])


# =============================================================================
# LINKEDIN SERVICE
# =============================================================================

class LinkedInService:
    """
    Servizio per pubblicazione su LinkedIn.

    Usa l'API v2 di LinkedIn per:
    - Autenticazione OAuth
    - Pubblicazione post (testo, media, articoli)
    - Post su company page
    - Recupero profilo e analytics base
    """

    AUTH_URL = "https://www.linkedin.com/oauth/v2"
    API_URL = "https://api.linkedin.com/v2"
    REST_API_URL = "https://api.linkedin.com/rest"

    def __init__(self):
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "https://markettina.it/api/v1/auth/linkedin/callback")
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def is_configured(self) -> bool:
        """Verifica se il servizio è configurato."""
        return bool(self.client_id and self.client_secret)

    @property
    def has_token(self) -> bool:
        """Verifica se abbiamo un token valido."""
        return bool(self.access_token)

    async def get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if not self._client:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    # =========================================================================
    # OAUTH
    # =========================================================================

    def get_authorization_url(self, state: str = "linkedin_auth") -> str:
        """
        Genera URL per autorizzazione OAuth.

        L'utente viene rediretto a questo URL per autorizzare l'app.
        """
        scopes = " ".join([
            "openid",
            "profile",
            "email",
            "w_member_social"
        ])

        return (
            f"{self.AUTH_URL}/authorization"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&state={state}"
            f"&scope={scopes}"
        )

    async def exchange_code_for_token(self, code: str) -> dict[str, Any]:
        """
        Scambia il code OAuth per un access token.
        """
        client = await self.get_client()

        response = await client.post(
            f"{self.AUTH_URL}/accessToken",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code != 200:
            logger.error("linkedin_token_exchange_failed", error=response.text)
            raise ValueError(f"Token exchange failed: {response.text}")

        data = response.json()
        self.access_token = data.get("access_token")

        logger.info("linkedin_token_obtained", expires_in=data.get("expires_in"))
        return data

    async def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Refresh access token."""
        client = await self.get_client()

        response = await client.post(
            f"{self.AUTH_URL}/accessToken",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
        )

        data = response.json()
        self.access_token = data.get("access_token")
        return data

    # =========================================================================
    # PROFILE
    # =========================================================================

    async def get_profile(self) -> LinkedInProfile:
        """Ottiene il profilo dell'utente autenticato."""
        if not self.has_token:
            raise ValueError("No access token. Please authenticate first.")

        client = await self.get_client()

        # Get basic profile
        response = await client.get(
            f"{self.API_URL}/userinfo",
            headers={
                "Authorization": f"Bearer {self.access_token}",
            }
        )

        if response.status_code != 200:
            raise ValueError(f"Profile fetch failed: {response.text}")

        data = response.json()

        return LinkedInProfile(
            id=data.get("sub", ""),
            first_name=data.get("given_name", ""),
            last_name=data.get("family_name", ""),
            profile_picture_url=data.get("picture"),
        )

    async def get_member_urn(self) -> str:
        """Ottiene l'URN del membro per posting."""
        profile = await self.get_profile()
        return f"urn:li:person:{profile.id}"

    # =========================================================================
    # POSTING
    # =========================================================================

    async def create_text_post(
        self,
        text: str,
        visibility: LinkedInVisibility = LinkedInVisibility.ANYONE
    ) -> LinkedInPostResponse:
        """
        Crea un post di solo testo.
        """
        if not self.has_token:
            return LinkedInPostResponse(
                success=False,
                error="No access token. Please authenticate first."
            )

        try:
            author_urn = await self.get_member_urn()

            client = await self.get_client()

            payload = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility.value
                }
            }

            response = await client.post(
                f"{self.API_URL}/ugcPosts",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0",
                }
            )

            if response.status_code in [200, 201]:
                post_id = response.headers.get("x-restli-id", "")
                logger.info("linkedin_post_created", post_id=post_id)
                return LinkedInPostResponse(
                    success=True,
                    post_id=post_id,
                    post_url=f"https://www.linkedin.com/feed/update/{post_id}"
                )
            else:
                error_msg = response.text[:200]
                logger.error("linkedin_post_failed", error=error_msg)
                return LinkedInPostResponse(success=False, error=error_msg)

        except Exception as e:
            logger.error("linkedin_post_error", error=str(e))
            return LinkedInPostResponse(success=False, error=str(e))

    async def create_image_post(
        self,
        text: str,
        image_url: str,
        visibility: LinkedInVisibility = LinkedInVisibility.ANYONE
    ) -> LinkedInPostResponse:
        """
        Crea un post con immagine.

        Flow:
        1. Register upload
        2. Upload image
        3. Create post with image asset
        """
        if not self.has_token:
            return LinkedInPostResponse(
                success=False,
                error="No access token. Please authenticate first."
            )

        try:
            author_urn = await self.get_member_urn()
            client = await self.get_client()

            # Step 1: Register upload
            register_payload = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": author_urn,
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }

            register_response = await client.post(
                f"{self.API_URL}/assets?action=registerUpload",
                json=register_payload,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                }
            )

            if register_response.status_code != 200:
                return LinkedInPostResponse(
                    success=False,
                    error=f"Upload registration failed: {register_response.text[:100]}"
                )

            register_data = register_response.json()
            upload_url = register_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
            asset_urn = register_data["value"]["asset"]

            # Step 2: Download image and upload to LinkedIn
            image_response = await client.get(image_url)
            if image_response.status_code != 200:
                return LinkedInPostResponse(
                    success=False,
                    error="Failed to download image"
                )

            image_data = image_response.content
            content_type = image_response.headers.get("content-type", "image/jpeg")

            upload_response = await client.put(
                upload_url,
                content=image_data,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": content_type,
                }
            )

            if upload_response.status_code not in [200, 201]:
                return LinkedInPostResponse(
                    success=False,
                    error=f"Image upload failed: {upload_response.status_code}"
                )

            # Step 3: Create post with image
            post_payload = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "media": asset_urn,
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility.value
                }
            }

            post_response = await client.post(
                f"{self.API_URL}/ugcPosts",
                json=post_payload,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0",
                }
            )

            if post_response.status_code in [200, 201]:
                post_id = post_response.headers.get("x-restli-id", "")
                logger.info("linkedin_image_post_created", post_id=post_id)
                return LinkedInPostResponse(
                    success=True,
                    post_id=post_id,
                    post_url=f"https://www.linkedin.com/feed/update/{post_id}"
                )
            else:
                return LinkedInPostResponse(
                    success=False,
                    error=f"Post creation failed: {post_response.text[:100]}"
                )

        except Exception as e:
            logger.error("linkedin_image_post_error", error=str(e))
            return LinkedInPostResponse(success=False, error=str(e))

    async def create_article_post(
        self,
        text: str,
        article_url: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        visibility: LinkedInVisibility = LinkedInVisibility.ANYONE
    ) -> LinkedInPostResponse:
        """
        Crea un post con link a un articolo.

        LinkedIn automaticamente genera preview del link.
        """
        if not self.has_token:
            return LinkedInPostResponse(
                success=False,
                error="No access token. Please authenticate first."
            )

        try:
            author_urn = await self.get_member_urn()
            client = await self.get_client()

            payload = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "ARTICLE",
                        "media": [
                            {
                                "status": "READY",
                                "originalUrl": article_url,
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility.value
                }
            }

            # Add optional title/description if provided
            if title:
                payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"][0]["title"] = {
                    "text": title
                }
            if description:
                payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"][0]["description"] = {
                    "text": description
                }

            response = await client.post(
                f"{self.API_URL}/ugcPosts",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0",
                }
            )

            if response.status_code in [200, 201]:
                post_id = response.headers.get("x-restli-id", "")
                logger.info("linkedin_article_post_created", post_id=post_id)
                return LinkedInPostResponse(
                    success=True,
                    post_id=post_id,
                    post_url=f"https://www.linkedin.com/feed/update/{post_id}"
                )
            else:
                return LinkedInPostResponse(
                    success=False,
                    error=f"Article post failed: {response.text[:100]}"
                )

        except Exception as e:
            logger.error("linkedin_article_post_error", error=str(e))
            return LinkedInPostResponse(success=False, error=str(e))

    # =========================================================================
    # UNIFIED PUBLISH
    # =========================================================================

    async def publish(self, request: LinkedInPostRequest) -> LinkedInPostResponse:
        """
        Metodo unificato per pubblicazione.

        Sceglie automaticamente il tipo di post basandosi sulla request.
        """
        if request.media_type == LinkedInMediaType.NONE:
            return await self.create_text_post(
                text=request.text,
                visibility=request.visibility
            )
        elif request.media_type == LinkedInMediaType.IMAGE and request.media_url:
            return await self.create_image_post(
                text=request.text,
                image_url=request.media_url,
                visibility=request.visibility
            )
        elif request.media_type == LinkedInMediaType.ARTICLE and request.article_url:
            return await self.create_article_post(
                text=request.text,
                article_url=request.article_url,
                title=request.media_title,
                description=request.media_description,
                visibility=request.visibility
            )
        else:
            return LinkedInPostResponse(
                success=False,
                error=f"Unsupported media type: {request.media_type}"
            )

    # =========================================================================
    # ANALYTICS (Basic)
    # =========================================================================

    async def get_post_stats(self, post_urn: str) -> dict[str, Any]:
        """
        Ottiene statistiche base di un post.

        Nota: Richiede permessi aggiuntivi per analytics completi.
        """
        if not self.has_token:
            return {"error": "Not authenticated"}

        try:
            client = await self.get_client()

            # Get social actions (likes, comments, shares)
            response = await client.get(
                f"{self.API_URL}/socialActions/{post_urn}",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                }
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "likes": data.get("likesSummary", {}).get("totalLikes", 0),
                    "comments": data.get("commentsSummary", {}).get("totalFirstLevelComments", 0),
                }
            else:
                return {"error": response.text[:100]}

        except Exception as e:
            return {"error": str(e)}


# =============================================================================
# SINGLETON
# =============================================================================

linkedin_service = LinkedInService()
