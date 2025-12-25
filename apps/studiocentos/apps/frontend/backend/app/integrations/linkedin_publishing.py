"""
LinkedIn Publishing Service - LinkedIn Marketing API Integration.

Servizio completo per pubblicazione su LinkedIn Personal Profile e Company Pages.
Utilizza LinkedIn Marketing API v2 per post, immagini, articoli e analytics.

PREREQUISITI:
- LinkedIn Developer App con prodotti:
  - Share on LinkedIn
  - Marketing Developer Platform (opzionale per analytics)
- OAuth 2.0 flow implementato
- Scopes: w_member_social, r_liteprofile, r_organization_social

REFERENCE:
- https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api
- https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/images-api

RATE LIMITS:
- UGC Posts: 100 posts/day per member
- API Calls: 100,000 calls/day
- Image Upload: Max 8MB per image
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode
import base64

import httpx
import structlog
from pydantic import BaseModel, Field

from app.core.config import settings

logger = structlog.get_logger(__name__)


# =============================================================================
# ENUMS
# =============================================================================


class Visibility(str, Enum):
    """Visibilità post LinkedIn."""
    PUBLIC = "PUBLIC"
    CONNECTIONS = "CONNECTIONS"
    LOGGED_IN = "LOGGED_IN"


class MediaCategory(str, Enum):
    """Categoria media per post."""
    NONE = "NONE"
    ARTICLE = "ARTICLE"
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    DOCUMENT = "DOCUMENT"


class AssetStatus(str, Enum):
    """Stato asset upload."""
    WAITING_UPLOAD = "WAITING_UPLOAD"
    PROCESSING = "PROCESSING"
    AVAILABLE = "AVAILABLE"
    FAILED = "FAILED"


# =============================================================================
# PYDANTIC MODELS
# =============================================================================


class TokenResponse(BaseModel):
    """Response OAuth token."""
    access_token: str
    expires_in: int  # seconds
    refresh_token: Optional[str] = None
    refresh_token_expires_in: Optional[int] = None
    scope: Optional[str] = None
    token_type: str = "Bearer"
    obtained_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def expires_at(self) -> datetime:
        """Calcola data scadenza token."""
        return self.obtained_at + timedelta(seconds=self.expires_in)

    @property
    def is_expired(self) -> bool:
        """Verifica se token è scaduto."""
        return datetime.utcnow() >= self.expires_at


class LinkedInProfile(BaseModel):
    """Profilo LinkedIn."""
    id: str
    first_name: str
    last_name: str
    headline: Optional[str] = None
    profile_picture_url: Optional[str] = None
    vanity_name: Optional[str] = None  # linkedin.com/in/{vanity_name}
    email: Optional[str] = None


class Organization(BaseModel):
    """Company Page LinkedIn."""
    id: str
    name: str
    vanity_name: Optional[str] = None
    logo_url: Optional[str] = None
    role: str = "ADMINISTRATOR"  # Role dell'utente nella org


class PostContent(BaseModel):
    """Contenuto post."""
    text: str = Field(..., min_length=1, max_length=3000)
    visibility: Visibility = Visibility.PUBLIC
    media_category: MediaCategory = MediaCategory.NONE

    # Per IMAGE/VIDEO
    media_url: Optional[str] = None
    media_title: Optional[str] = None
    media_description: Optional[str] = None

    # Per ARTICLE
    article_url: Optional[str] = None
    article_title: Optional[str] = None
    article_description: Optional[str] = None
    article_thumbnail_url: Optional[str] = None


class PostResult(BaseModel):
    """Risultato pubblicazione."""
    success: bool
    post_id: Optional[str] = None
    post_urn: Optional[str] = None
    post_url: Optional[str] = None
    error: Optional[str] = None
    published_at: Optional[datetime] = None


class PostAnalytics(BaseModel):
    """Analytics post."""
    post_urn: str
    impressions: int = 0
    clicks: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    engagement_rate: float = 0.0
    fetched_at: datetime = Field(default_factory=datetime.utcnow)


class LinkedInStatus(BaseModel):
    """Stato connessione LinkedIn."""
    connected: bool = False
    profile: Optional[LinkedInProfile] = None
    organizations: List[Organization] = Field(default_factory=list)
    token_valid: bool = False
    token_expires_at: Optional[datetime] = None
    scopes: List[str] = Field(default_factory=list)
    error: Optional[str] = None


# =============================================================================
# LINKEDIN PUBLISHING SERVICE
# =============================================================================


class LinkedInPublishingService:
    """
    Servizio completo per pubblicazione LinkedIn.

    Features:
    - OAuth 2.0 authentication
    - Post testuali
    - Post con immagine (upload)
    - Post con articolo (link preview)
    - Company Page publishing
    - Basic analytics

    Usage:
        service = LinkedInPublishingService()

        # Verifica connessione
        status = await service.get_status()

        # Pubblica post testo
        result = await service.publish_text_post("Hello LinkedIn!")

        # Pubblica con immagine
        result = await service.publish_image_post(
            text="Nuovo progetto!",
            image_url="https://example.com/image.jpg"
        )
    """

    BASE_URL = "https://api.linkedin.com/v2"
    AUTH_URL = "https://www.linkedin.com/oauth/v2"

    # OAuth scopes
    DEFAULT_SCOPES = [
        "openid",
        "profile",
        "email",
        "w_member_social"  # Richiesto per posting
    ]

    def __init__(self):
        self.client_id = settings.LINKEDIN_CLIENT_ID
        self.client_secret = settings.LINKEDIN_CLIENT_SECRET
        self.redirect_uri = settings.LINKEDIN_REDIRECT_URI or f"{settings.BACKEND_URL}/api/v1/social/linkedin/auth/callback"
        self.access_token = settings.LINKEDIN_ACCESS_TOKEN
        self._client: Optional[httpx.AsyncClient] = None
        self._profile_cache: Optional[LinkedInProfile] = None
        self._person_urn: Optional[str] = None

    @property
    def is_configured(self) -> bool:
        """Verifica se le credenziali OAuth sono configurate."""
        return bool(self.client_id and self.client_secret)

    @property
    def has_token(self) -> bool:
        """Verifica se ha access token."""
        return bool(self.access_token)

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                follow_redirects=True
            )
        return self._client

    async def close(self) -> None:
        """Chiudi HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _get_headers(self) -> Dict[str, str]:
        """Headers per richieste autenticate."""
        if not self.access_token:
            raise LinkedInAPIError("Access token non configurato")

        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202304"
        }

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Esegue richiesta a LinkedIn API.

        Args:
            method: HTTP method
            endpoint: Endpoint relativo
            data: Body JSON
            params: Query parameters
            headers: Headers aggiuntivi

        Returns:
            Response JSON
        """
        url = f"{self.BASE_URL}{endpoint}"
        request_headers = self._get_headers()
        if headers:
            request_headers.update(headers)

        client = await self._get_client()

        try:
            if method == "GET":
                response = await client.get(url, params=params, headers=request_headers)
            elif method == "POST":
                response = await client.post(url, json=data, params=params, headers=request_headers)
            elif method == "DELETE":
                response = await client.delete(url, headers=request_headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            # LinkedIn returns 201 for created resources
            if response.status_code not in [200, 201, 204]:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("message", response.text)

                logger.error(
                    "linkedin_api_error",
                    endpoint=endpoint,
                    status=response.status_code,
                    error=error_msg
                )

                raise LinkedInAPIError(
                    f"LinkedIn API Error [{response.status_code}]: {error_msg}",
                    status_code=response.status_code
                )

            if response.status_code == 204:
                return {}

            return response.json() if response.content else {}

        except httpx.TimeoutException:
            logger.error("linkedin_api_timeout", endpoint=endpoint)
            raise LinkedInAPIError("LinkedIn API timeout")
        except httpx.RequestError as e:
            logger.error("linkedin_api_request_error", endpoint=endpoint, error=str(e))
            raise LinkedInAPIError(f"Request error: {str(e)}")

    # =========================================================================
    # OAUTH 2.0
    # =========================================================================

    def get_authorization_url(self, state: str) -> str:
        """
        Genera URL per autorizzazione OAuth.

        Args:
            state: State parameter per CSRF protection

        Returns:
            URL completo per redirect
        """
        if not self.is_configured:
            raise LinkedInAPIError("LinkedIn OAuth non configurato")

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "scope": " ".join(self.DEFAULT_SCOPES)
        }

        return f"{self.AUTH_URL}/authorization?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> TokenResponse:
        """
        Scambia authorization code per access token.

        Args:
            code: Authorization code da callback

        Returns:
            TokenResponse con access token
        """
        if not self.is_configured:
            raise LinkedInAPIError("LinkedIn OAuth non configurato")

        client = await self._get_client()

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        response = await client.post(
            f"{self.AUTH_URL}/accessToken",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code != 200:
            error = response.json()
            raise LinkedInAPIError(
                f"Token exchange failed: {error.get('error_description', 'Unknown error')}"
            )

        token_data = response.json()

        token = TokenResponse(
            access_token=token_data["access_token"],
            expires_in=token_data.get("expires_in", 5184000),  # Default 60 days
            refresh_token=token_data.get("refresh_token"),
            refresh_token_expires_in=token_data.get("refresh_token_expires_in"),
            scope=token_data.get("scope")
        )

        # Update instance token
        self.access_token = token.access_token

        logger.info("linkedin_token_obtained", expires_in=token.expires_in)

        return token

    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Rinnova access token usando refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            TokenResponse con nuovo access token
        """
        if not self.is_configured:
            raise LinkedInAPIError("LinkedIn OAuth non configurato")

        client = await self._get_client()

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        response = await client.post(
            f"{self.AUTH_URL}/accessToken",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )

        if response.status_code != 200:
            error = response.json()
            raise LinkedInAPIError(
                f"Token refresh failed: {error.get('error_description', 'Unknown error')}"
            )

        token_data = response.json()

        token = TokenResponse(
            access_token=token_data["access_token"],
            expires_in=token_data.get("expires_in", 5184000),
            refresh_token=token_data.get("refresh_token"),
            refresh_token_expires_in=token_data.get("refresh_token_expires_in"),
            scope=token_data.get("scope")
        )

        self.access_token = token.access_token

        logger.info("linkedin_token_refreshed", expires_in=token.expires_in)

        return token

    # =========================================================================
    # PROFILE & ORGANIZATIONS
    # =========================================================================

    async def get_profile(self, use_cache: bool = True) -> LinkedInProfile:
        """
        Ottiene profilo utente corrente.

        Args:
            use_cache: Se usare cache

        Returns:
            LinkedInProfile
        """
        if use_cache and self._profile_cache:
            return self._profile_cache

        # Get basic profile
        data = await self._make_request(
            "GET",
            "/me",
            params={"projection": "(id,firstName,lastName,profilePicture(displayImage~:playableStreams))"}
        )

        # Get email (separate endpoint)
        email = None
        try:
            email_data = await self._make_request(
                "GET",
                "/emailAddress",
                params={"q": "members", "projection": "(elements*(handle~))"}
            )
            elements = email_data.get("elements", [])
            if elements:
                email = elements[0].get("handle~", {}).get("emailAddress")
        except Exception:
            pass  # Email optional

        profile = LinkedInProfile(
            id=data["id"],
            first_name=data.get("firstName", {}).get("localized", {}).get("en_US", ""),
            last_name=data.get("lastName", {}).get("localized", {}).get("en_US", ""),
            email=email
        )

        # Extract profile picture
        try:
            images = data.get("profilePicture", {}).get("displayImage~", {}).get("elements", [])
            if images:
                # Get largest image
                largest = max(images, key=lambda x: x.get("data", {}).get("com.linkedin.digitalmedia.mediaartifact.StillImage", {}).get("displaySize", {}).get("width", 0))
                identifiers = largest.get("identifiers", [])
                if identifiers:
                    profile.profile_picture_url = identifiers[0].get("identifier")
        except Exception:
            pass

        self._profile_cache = profile
        self._person_urn = f"urn:li:person:{profile.id}"

        logger.info(
            "linkedin_profile_fetched",
            name=f"{profile.first_name} {profile.last_name}"
        )

        return profile

    async def get_organizations(self) -> List[Organization]:
        """
        Ottiene Company Pages gestite dall'utente.

        Returns:
            Lista di Organization
        """
        try:
            data = await self._make_request(
                "GET",
                "/organizationAcls",
                params={
                    "q": "roleAssignee",
                    "role": "ADMINISTRATOR",
                    "projection": "(elements*(organization~(id,name,vanityName,logoV2(original~:playableStreams))))"
                }
            )

            organizations = []
            for element in data.get("elements", []):
                org_data = element.get("organization~", {})

                org = Organization(
                    id=str(org_data.get("id", "")),
                    name=org_data.get("name", {}).get("localized", {}).get("en_US", ""),
                    vanity_name=org_data.get("vanityName"),
                    role="ADMINISTRATOR"
                )

                # Extract logo
                try:
                    logo_data = org_data.get("logoV2", {}).get("original~", {})
                    elements = logo_data.get("elements", [])
                    if elements:
                        identifiers = elements[0].get("identifiers", [])
                        if identifiers:
                            org.logo_url = identifiers[0].get("identifier")
                except Exception:
                    pass

                organizations.append(org)

            logger.info("linkedin_organizations_fetched", count=len(organizations))

            return organizations

        except LinkedInAPIError:
            return []

    async def get_status(self) -> LinkedInStatus:
        """
        Ottiene stato connessione completo.

        Returns:
            LinkedInStatus
        """
        status = LinkedInStatus()

        if not self.has_token:
            status.error = "Access token non configurato"
            return status

        try:
            profile = await self.get_profile()
            organizations = await self.get_organizations()

            status.connected = True
            status.profile = profile
            status.organizations = organizations
            status.token_valid = True

            logger.info(
                "linkedin_status_ok",
                profile=f"{profile.first_name} {profile.last_name}",
                organizations=len(organizations)
            )

        except LinkedInAPIError as e:
            status.error = str(e)
            logger.warning("linkedin_status_error", error=str(e))

        return status

    # =========================================================================
    # IMAGE UPLOAD
    # =========================================================================

    async def _register_upload(self, owner_urn: str) -> Dict[str, Any]:
        """
        Registra upload per immagine.

        Args:
            owner_urn: URN del proprietario (person o organization)

        Returns:
            Dict con uploadUrl e asset URN
        """
        data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": owner_urn,
                "serviceRelationships": [{
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }]
            }
        }

        result = await self._make_request(
            "POST",
            "/assets?action=registerUpload",
            data=data
        )

        value = result.get("value", {})
        upload_mechanism = value.get("uploadMechanism", {})
        upload_url = upload_mechanism.get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}).get("uploadUrl")
        asset = value.get("asset")

        if not upload_url or not asset:
            raise LinkedInAPIError("Failed to get upload URL")

        return {
            "upload_url": upload_url,
            "asset": asset
        }

    async def _upload_image(self, upload_url: str, image_data: bytes) -> bool:
        """
        Carica immagine su LinkedIn CDN.

        Args:
            upload_url: URL presignato per upload
            image_data: Bytes immagine

        Returns:
            True se upload riuscito
        """
        client = await self._get_client()

        response = await client.put(
            upload_url,
            content=image_data,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/octet-stream"
            }
        )

        if response.status_code not in [200, 201]:
            raise LinkedInAPIError(f"Image upload failed: {response.status_code}")

        return True

    async def _download_and_upload_image(self, image_url: str, owner_urn: str) -> str:
        """
        Scarica immagine da URL e carica su LinkedIn.

        Args:
            image_url: URL immagine da scaricare
            owner_urn: URN proprietario

        Returns:
            Asset URN dell'immagine caricata
        """
        client = await self._get_client()

        # Download image
        response = await client.get(image_url)
        if response.status_code != 200:
            raise LinkedInAPIError(f"Failed to download image: {response.status_code}")

        image_data = response.content

        # Check size (max 8MB)
        if len(image_data) > 8 * 1024 * 1024:
            raise LinkedInAPIError("Image too large (max 8MB)")

        # Register upload
        upload_info = await self._register_upload(owner_urn)

        # Upload image
        await self._upload_image(upload_info["upload_url"], image_data)

        logger.info("linkedin_image_uploaded", asset=upload_info["asset"])

        return upload_info["asset"]

    # =========================================================================
    # PUBLISHING
    # =========================================================================

    async def _get_person_urn(self) -> str:
        """Ottiene URN persona corrente."""
        if self._person_urn:
            return self._person_urn

        profile = await self.get_profile()
        self._person_urn = f"urn:li:person:{profile.id}"
        return self._person_urn

    async def publish_text_post(
        self,
        text: str,
        visibility: Visibility = Visibility.PUBLIC
    ) -> PostResult:
        """
        Pubblica post di solo testo.

        Args:
            text: Testo del post (max 3000 caratteri)
            visibility: Visibilità del post

        Returns:
            PostResult
        """
        author = await self._get_person_urn()

        payload = {
            "author": author,
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

        try:
            result = await self._make_request("POST", "/ugcPosts", data=payload)

            post_id = result.get("id", "")

            return PostResult(
                success=True,
                post_id=post_id,
                post_urn=post_id,
                post_url=self._build_post_url(post_id),
                published_at=datetime.utcnow()
            )

        except LinkedInAPIError as e:
            return PostResult(
                success=False,
                error=str(e)
            )

    async def publish_image_post(
        self,
        text: str,
        image_url: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Visibility = Visibility.PUBLIC
    ) -> PostResult:
        """
        Pubblica post con immagine.

        Args:
            text: Testo del post
            image_url: URL immagine da caricare
            title: Titolo immagine (opzionale)
            description: Descrizione immagine (opzionale)
            visibility: Visibilità

        Returns:
            PostResult
        """
        author = await self._get_person_urn()

        try:
            # Upload image
            asset = await self._download_and_upload_image(image_url, author)

            # Create post with image
            media = [{
                "status": "READY",
                "description": {
                    "text": description or ""
                },
                "media": asset,
                "title": {
                    "text": title or ""
                }
            }]

            payload = {
                "author": author,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": media
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility.value
                }
            }

            result = await self._make_request("POST", "/ugcPosts", data=payload)

            post_id = result.get("id", "")

            logger.info("linkedin_image_post_published", post_id=post_id)

            return PostResult(
                success=True,
                post_id=post_id,
                post_urn=post_id,
                post_url=self._build_post_url(post_id),
                published_at=datetime.utcnow()
            )

        except LinkedInAPIError as e:
            return PostResult(
                success=False,
                error=str(e)
            )

    async def publish_article_post(
        self,
        text: str,
        article_url: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        visibility: Visibility = Visibility.PUBLIC
    ) -> PostResult:
        """
        Pubblica post con link (article preview).

        Args:
            text: Testo del post
            article_url: URL dell'articolo
            title: Titolo (opzionale, LinkedIn lo estrae automaticamente)
            description: Descrizione
            thumbnail_url: Thumbnail personalizzata
            visibility: Visibilità

        Returns:
            PostResult
        """
        author = await self._get_person_urn()

        try:
            media = [{
                "status": "READY",
                "originalUrl": article_url
            }]

            if title:
                media[0]["title"] = {"text": title}
            if description:
                media[0]["description"] = {"text": description}

            payload = {
                "author": author,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "ARTICLE",
                        "media": media
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": visibility.value
                }
            }

            result = await self._make_request("POST", "/ugcPosts", data=payload)

            post_id = result.get("id", "")

            logger.info("linkedin_article_post_published", post_id=post_id, url=article_url)

            return PostResult(
                success=True,
                post_id=post_id,
                post_urn=post_id,
                post_url=self._build_post_url(post_id),
                published_at=datetime.utcnow()
            )

        except LinkedInAPIError as e:
            return PostResult(
                success=False,
                error=str(e)
            )

    async def publish_to_company(
        self,
        organization_id: str,
        content: PostContent
    ) -> PostResult:
        """
        Pubblica su Company Page.

        Args:
            organization_id: ID organizzazione
            content: Contenuto post

        Returns:
            PostResult
        """
        org_urn = f"urn:li:organization:{organization_id}"

        try:
            # Build media based on category
            media = None

            if content.media_category == MediaCategory.IMAGE and content.media_url:
                asset = await self._download_and_upload_image(content.media_url, org_urn)
                media = [{
                    "status": "READY",
                    "media": asset,
                    "title": {"text": content.media_title or ""},
                    "description": {"text": content.media_description or ""}
                }]

            elif content.media_category == MediaCategory.ARTICLE and content.article_url:
                media = [{
                    "status": "READY",
                    "originalUrl": content.article_url,
                    "title": {"text": content.article_title or ""},
                    "description": {"text": content.article_description or ""}
                }]

            share_content = {
                "shareCommentary": {
                    "text": content.text
                },
                "shareMediaCategory": content.media_category.value
            }

            if media:
                share_content["media"] = media

            payload = {
                "author": org_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": share_content
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": content.visibility.value
                }
            }

            result = await self._make_request("POST", "/ugcPosts", data=payload)

            post_id = result.get("id", "")

            logger.info(
                "linkedin_company_post_published",
                organization=organization_id,
                post_id=post_id
            )

            return PostResult(
                success=True,
                post_id=post_id,
                post_urn=post_id,
                post_url=self._build_post_url(post_id),
                published_at=datetime.utcnow()
            )

        except LinkedInAPIError as e:
            return PostResult(
                success=False,
                error=str(e)
            )

    async def publish(self, content: PostContent) -> PostResult:
        """
        Pubblicazione unificata basata su contenuto.

        Args:
            content: PostContent con tutti i dettagli

        Returns:
            PostResult
        """
        if content.media_category == MediaCategory.NONE:
            return await self.publish_text_post(
                text=content.text,
                visibility=content.visibility
            )
        elif content.media_category == MediaCategory.IMAGE and content.media_url:
            return await self.publish_image_post(
                text=content.text,
                image_url=content.media_url,
                title=content.media_title,
                description=content.media_description,
                visibility=content.visibility
            )
        elif content.media_category == MediaCategory.ARTICLE and content.article_url:
            return await self.publish_article_post(
                text=content.text,
                article_url=content.article_url,
                title=content.article_title,
                description=content.article_description,
                visibility=content.visibility
            )
        else:
            return PostResult(
                success=False,
                error=f"Unsupported media category: {content.media_category}"
            )

    # =========================================================================
    # ANALYTICS
    # =========================================================================

    async def get_post_analytics(self, post_urn: str) -> PostAnalytics:
        """
        Ottiene analytics per un post.

        NOTA: Richiede Marketing Developer Platform product.

        Args:
            post_urn: URN del post

        Returns:
            PostAnalytics
        """
        analytics = PostAnalytics(post_urn=post_urn)

        try:
            # Social actions (likes, comments, shares)
            data = await self._make_request(
                "GET",
                "/socialActions",
                params={
                    "q": "entity",
                    "entity": post_urn,
                    "projection": "(likesSummary,commentsSummary)"
                }
            )

            analytics.likes = data.get("likesSummary", {}).get("totalLikes", 0)
            analytics.comments = data.get("commentsSummary", {}).get("totalComments", 0)

        except LinkedInAPIError as e:
            logger.warning("linkedin_analytics_error", post_urn=post_urn, error=str(e))

        return analytics

    # =========================================================================
    # HELPERS
    # =========================================================================

    def _build_post_url(self, post_urn: str) -> str:
        """Costruisce URL pubblico del post."""
        # Extract activity ID from URN
        # urn:li:share:1234567890 -> 1234567890
        parts = post_urn.split(":")
        if len(parts) >= 4:
            activity_id = parts[-1]
            return f"https://www.linkedin.com/feed/update/{post_urn}"
        return f"https://www.linkedin.com/feed/update/{post_urn}"


# =============================================================================
# EXCEPTIONS
# =============================================================================


class LinkedInAPIError(Exception):
    """Errore API LinkedIn."""

    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_linkedin_service: Optional[LinkedInPublishingService] = None


def get_linkedin_publishing_service() -> LinkedInPublishingService:
    """Get singleton instance of LinkedInPublishingService."""
    global _linkedin_service
    if _linkedin_service is None:
        _linkedin_service = LinkedInPublishingService()
    return _linkedin_service
