"""
Google Business Profile API Service (ex Google My Business)
Real implementation using My Business API
"""
import logging
from datetime import date, datetime, timedelta
from typing import Any, Optional

import httpx
from sqlalchemy.orm import Session

from app.domain.auth.oauth_tokens import OAuthProvider, OAuthTokenService

from .schemas import (
    GMBDashboardResponse,
    GMBInsightsData,
    GMBInsightsResponse,
    GMBLocationInfo,
    GMBPost,
    GMBPostCreate,
    GMBPostsResponse,
    GMBPostType,
    GMBReview,
    GMBReviewsResponse,
)

logger = logging.getLogger(__name__)

# Google Business Profile API Base URLs
GMB_API_BASE = "https://mybusinessbusinessinformation.googleapis.com/v1"
GMB_REVIEWS_API = "https://mybusiness.googleapis.com/v4"
GMB_ACCOUNT_API = "https://mybusinessaccountmanagement.googleapis.com/v1"


class GoogleBusinessProfileService:
    """Service for Google Business Profile API (GMB)."""

    def __init__(
        self,
        access_token: str,
        account_id: str | None = None,
        location_id: str | None = None
    ):
        """
        Initialize GMB service.

        Args:
            access_token: Valid Google OAuth access token with business.manage scope
            account_id: GMB account ID (format: accounts/XXXXXX)
            location_id: GMB location ID (format: locations/XXXXXX)
        """
        self.access_token = access_token
        self.account_id = account_id
        self.location_id = location_id
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    @classmethod
    def from_admin_token(
        cls,
        db: Session,
        admin_id: int,
        account_id: str | None = None,
        location_id: str | None = None
    ) -> Optional["GoogleBusinessProfileService"]:
        """
        Create service instance from admin's stored OAuth token.

        Args:
            db: Database session
            admin_id: Admin user ID
            account_id: Optional GMB account ID
            location_id: Optional GMB location ID

        Returns:
            GoogleBusinessProfileService instance or None if no valid token
        """
        token = OAuthTokenService.get_valid_token(db, admin_id, OAuthProvider.GOOGLE)
        if not token:
            logger.warning(f"No valid Google OAuth token for admin {admin_id}")
            return None
        return cls(access_token=token, account_id=account_id, location_id=location_id)

    async def list_accounts(self) -> list[dict[str, Any]]:
        """List available GMB accounts."""
        url = f"{GMB_ACCOUNT_API}/accounts"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=30.0)

                if response.status_code != 200:
                    logger.error(f"Error listing GMB accounts: {response.status_code} - {response.text}")
                    return []

                data = response.json()
                return data.get("accounts", [])

        except Exception as e:
            logger.error(f"Error listing GMB accounts: {e}", exc_info=True)
            return []

    async def list_locations(self, account_id: str | None = None) -> list[dict[str, Any]]:
        """List locations for an account."""
        account = account_id or self.account_id
        if not account:
            logger.error("No account ID provided")
            return []

        # Format account ID if needed
        if not account.startswith("accounts/"):
            account = f"accounts/{account}"

        url = f"{GMB_API_BASE}/{account}/locations"
        params = {"readMask": "name,title,storefrontAddress,phoneNumbers,websiteUri,metadata"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Error listing GMB locations: {response.status_code} - {response.text}")
                    return []

                data = response.json()
                return data.get("locations", [])

        except Exception as e:
            logger.error(f"Error listing GMB locations: {e}", exc_info=True)
            return []

    async def get_location(self, location_name: str | None = None) -> GMBLocationInfo | None:
        """Get location details."""
        location = location_name or self.location_id
        if not location:
            logger.error("No location ID provided")
            return None

        # Format location name if needed
        if not location.startswith("locations/"):
            location = f"locations/{location}"

        url = f"{GMB_API_BASE}/{location}"
        params = {"readMask": "name,title,storefrontAddress,phoneNumbers,websiteUri,metadata"}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Error getting GMB location: {response.status_code} - {response.text}")
                    return None

                data = response.json()
                return self._parse_location(data)

        except Exception as e:
            logger.error(f"Error getting GMB location: {e}", exc_info=True)
            return None

    def _parse_location(self, data: dict[str, Any]) -> GMBLocationInfo:
        """Parse location response into GMBLocationInfo."""
        address = data.get("storefrontAddress", {})
        address_dict = {
            "street": " ".join(address.get("addressLines", [])),
            "city": address.get("locality", ""),
            "region": address.get("administrativeArea", ""),
            "postal_code": address.get("postalCode", ""),
            "country": address.get("regionCode", ""),
        }

        phone_numbers = data.get("phoneNumbers", {})
        primary_phone = phone_numbers.get("primaryPhone", "")

        metadata = data.get("metadata", {})

        return GMBLocationInfo(
            name=data.get("name", ""),
            title=data.get("title", ""),
            store_code=data.get("storeCode"),
            address=address_dict,
            phone_number=primary_phone,
            website_uri=data.get("websiteUri"),
            is_verified=metadata.get("hasGoogleUpdated", False)
        )

    async def get_reviews(
        self,
        location_name: str | None = None,
        page_size: int = 50,
        page_token: str | None = None
    ) -> GMBReviewsResponse:
        """
        Get reviews for a location.

        Args:
            location_name: Location identifier
            page_size: Number of reviews per page
            page_token: Token for pagination

        Returns:
            GMBReviewsResponse with reviews list
        """
        location = location_name or self.location_id
        if not location:
            logger.error("No location ID provided")
            return GMBReviewsResponse()

        # Format for v4 API
        account = self.account_id or ""
        if not account.startswith("accounts/"):
            account = f"accounts/{account}"
        if not location.startswith("locations/"):
            location = f"locations/{location}"

        url = f"{GMB_REVIEWS_API}/{account}/{location}/reviews"
        params = {"pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Error getting GMB reviews: {response.status_code} - {response.text}")
                    return GMBReviewsResponse()

                data = response.json()
                return self._parse_reviews_response(data)

        except Exception as e:
            logger.error(f"Error getting GMB reviews: {e}", exc_info=True)
            return GMBReviewsResponse()

    def _parse_reviews_response(self, data: dict[str, Any]) -> GMBReviewsResponse:
        """Parse reviews API response."""
        reviews = []

        for review_data in data.get("reviews", []):
            reviewer = review_data.get("reviewer", {})

            # Parse star rating
            rating_str = review_data.get("starRating", "FIVE")
            rating_map = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}
            star_rating = rating_map.get(rating_str, 5)

            # Parse reply
            reply_data = review_data.get("reviewReply", {})
            reply_text = reply_data.get("comment")
            reply_time = None
            if reply_data.get("updateTime"):
                try:
                    reply_time = datetime.fromisoformat(reply_data["updateTime"].replace("Z", "+00:00"))
                except ValueError:
                    pass

            # Parse create time
            create_time = datetime.utcnow()
            if review_data.get("createTime"):
                try:
                    create_time = datetime.fromisoformat(review_data["createTime"].replace("Z", "+00:00"))
                except ValueError:
                    pass

            reviews.append(GMBReview(
                review_id=review_data.get("reviewId", review_data.get("name", "")),
                reviewer_name=reviewer.get("displayName", "Anonymous"),
                reviewer_photo_url=reviewer.get("profilePhotoUrl"),
                star_rating=star_rating,
                comment=review_data.get("comment"),
                create_time=create_time,
                reply=reply_text,
                reply_time=reply_time
            ))

        # Calculate average rating
        total_rating = sum(r.star_rating for r in reviews)
        avg_rating = round(total_rating / len(reviews), 1) if reviews else 0.0

        return GMBReviewsResponse(
            reviews=reviews,
            average_rating=avg_rating,
            total_reviews=data.get("totalReviewCount", len(reviews)),
            next_page_token=data.get("nextPageToken")
        )

    async def reply_to_review(
        self,
        review_id: str,
        reply_text: str,
        location_name: str | None = None
    ) -> bool:
        """
        Reply to a review.

        Args:
            review_id: Review identifier
            reply_text: Reply message
            location_name: Location identifier

        Returns:
            True if reply was successful
        """
        location = location_name or self.location_id
        if not location:
            logger.error("No location ID provided")
            return False

        account = self.account_id or ""
        if not account.startswith("accounts/"):
            account = f"accounts/{account}"
        if not location.startswith("locations/"):
            location = f"locations/{location}"

        url = f"{GMB_REVIEWS_API}/{account}/{location}/reviews/{review_id}/reply"
        body = {"comment": reply_text}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    url,
                    headers=self.headers,
                    json=body,
                    timeout=30.0
                )

                if response.status_code not in [200, 201]:
                    logger.error(f"Error replying to review: {response.status_code} - {response.text}")
                    return False

                return True

        except Exception as e:
            logger.error(f"Error replying to review: {e}", exc_info=True)
            return False

    async def create_post(
        self,
        post_data: GMBPostCreate,
        location_name: str | None = None
    ) -> GMBPost | None:
        """
        Create a new post on GMB.

        Args:
            post_data: Post content and metadata
            location_name: Location identifier

        Returns:
            Created GMBPost or None if failed
        """
        location = location_name or self.location_id
        if not location:
            logger.error("No location ID provided")
            return None

        account = self.account_id or ""
        if not account.startswith("accounts/"):
            account = f"accounts/{account}"
        if not location.startswith("locations/"):
            location = f"locations/{location}"

        url = f"{GMB_REVIEWS_API}/{account}/{location}/localPosts"

        # Build post body
        body = {
            "summary": post_data.summary,
            "languageCode": "it",
            "topicType": post_data.post_type.value if post_data.post_type != GMBPostType.STANDARD else "STANDARD"
        }

        # Add media if provided
        if post_data.media_urls:
            body["media"] = [
                {"mediaFormat": "PHOTO", "sourceUrl": url}
                for url in post_data.media_urls
            ]

        # Add call to action
        if post_data.call_to_action and post_data.action_url:
            body["callToAction"] = {
                "actionType": post_data.call_to_action.value,
                "url": post_data.action_url
            }

        # Add event details if event post
        if post_data.post_type == GMBPostType.EVENT and post_data.event_title:
            body["event"] = {
                "title": post_data.event_title,
                "schedule": {
                    "startDate": {
                        "year": post_data.event_start.year,
                        "month": post_data.event_start.month,
                        "day": post_data.event_start.day
                    } if post_data.event_start else None,
                    "endDate": {
                        "year": post_data.event_end.year,
                        "month": post_data.event_end.month,
                        "day": post_data.event_end.day
                    } if post_data.event_end else None
                }
            }

        # Add offer details if offer post
        if post_data.post_type == GMBPostType.OFFER:
            body["offer"] = {
                "couponCode": post_data.offer_code,
                "termsConditions": post_data.offer_terms
            }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=body,
                    timeout=30.0
                )

                if response.status_code not in [200, 201]:
                    logger.error(f"Error creating GMB post: {response.status_code} - {response.text}")
                    return None

                data = response.json()
                return self._parse_post(data)

        except Exception as e:
            logger.error(f"Error creating GMB post: {e}", exc_info=True)
            return None

    async def get_posts(
        self,
        location_name: str | None = None,
        page_size: int = 20,
        page_token: str | None = None
    ) -> GMBPostsResponse:
        """Get posts for a location."""
        location = location_name or self.location_id
        if not location:
            logger.error("No location ID provided")
            return GMBPostsResponse()

        account = self.account_id or ""
        if not account.startswith("accounts/"):
            account = f"accounts/{account}"
        if not location.startswith("locations/"):
            location = f"locations/{location}"

        url = f"{GMB_REVIEWS_API}/{account}/{location}/localPosts"
        params = {"pageSize": page_size}
        if page_token:
            params["pageToken"] = page_token

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.error(f"Error getting GMB posts: {response.status_code} - {response.text}")
                    return GMBPostsResponse()

                data = response.json()
                posts = [self._parse_post(p) for p in data.get("localPosts", [])]

                return GMBPostsResponse(
                    posts=posts,
                    total_posts=len(posts),
                    next_page_token=data.get("nextPageToken")
                )

        except Exception as e:
            logger.error(f"Error getting GMB posts: {e}", exc_info=True)
            return GMBPostsResponse()

    def _parse_post(self, data: dict[str, Any]) -> GMBPost:
        """Parse post data into GMBPost."""
        # Parse create time
        create_time = datetime.utcnow()
        if data.get("createTime"):
            try:
                create_time = datetime.fromisoformat(data["createTime"].replace("Z", "+00:00"))
            except ValueError:
                pass

        # Parse update time
        update_time = None
        if data.get("updateTime"):
            try:
                update_time = datetime.fromisoformat(data["updateTime"].replace("Z", "+00:00"))
            except ValueError:
                pass

        # Parse media URLs
        media_urls = []
        for media in data.get("media", []):
            if media.get("googleUrl"):
                media_urls.append(media["googleUrl"])
            elif media.get("sourceUrl"):
                media_urls.append(media["sourceUrl"])

        # Parse call to action
        cta = data.get("callToAction", {})

        # Parse metrics
        search_url = data.get("searchUrl", "")

        return GMBPost(
            post_id=data.get("name", "").split("/")[-1],
            summary=data.get("summary", ""),
            post_type=GMBPostType(data.get("topicType", "STANDARD")),
            create_time=create_time,
            update_time=update_time,
            media_urls=media_urls,
            call_to_action=cta.get("actionType"),
            action_url=cta.get("url"),
            state=data.get("state", "LIVE")
        )

    async def get_insights(
        self,
        location_name: str | None = None,
        days: int = 30
    ) -> GMBInsightsResponse:
        """
        Get insights/analytics for a location.

        Note: Google Business Profile Insights API has been deprecated.
        This method uses the Performance API as a replacement.
        """
        location = location_name or self.location_id
        if not location:
            logger.error("No location ID provided")
            return GMBInsightsResponse(
                location_name="",
                period_start=date.today() - timedelta(days=days),
                period_end=date.today()
            )

        # Use the new Performance API
        url = f"https://businessprofileperformance.googleapis.com/v1/{location}:getDailyMetricsTimeSeries"

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        params = {
            "dailyMetric": [
                "BUSINESS_IMPRESSIONS_DESKTOP_MAPS",
                "BUSINESS_IMPRESSIONS_DESKTOP_SEARCH",
                "BUSINESS_IMPRESSIONS_MOBILE_MAPS",
                "BUSINESS_IMPRESSIONS_MOBILE_SEARCH",
                "CALL_CLICKS",
                "WEBSITE_CLICKS",
                "BUSINESS_DIRECTION_REQUESTS"
            ],
            "dailyRange.startDate.year": start_date.year,
            "dailyRange.startDate.month": start_date.month,
            "dailyRange.startDate.day": start_date.day,
            "dailyRange.endDate.year": end_date.year,
            "dailyRange.endDate.month": end_date.month,
            "dailyRange.endDate.day": end_date.day
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )

                if response.status_code != 200:
                    logger.warning(f"GMB Performance API error: {response.status_code} - {response.text}")
                    # Return empty insights
                    return GMBInsightsResponse(
                        location_name=location,
                        period_start=start_date,
                        period_end=end_date
                    )

                data = response.json()
                return self._parse_insights(data, location, start_date, end_date)

        except Exception as e:
            logger.error(f"Error getting GMB insights: {e}", exc_info=True)
            return GMBInsightsResponse(
                location_name=location,
                period_start=start_date,
                period_end=end_date
            )

    def _parse_insights(
        self,
        data: dict[str, Any],
        location: str,
        start_date: date,
        end_date: date
    ) -> GMBInsightsResponse:
        """Parse insights data."""
        metrics_breakdown = []

        # Aggregate totals
        total_searches = 0
        maps_views = 0
        search_views = 0
        website_clicks = 0
        phone_calls = 0
        direction_requests = 0

        for series in data.get("multiDailyMetricTimeSeries", []):
            metric_name = series.get("dailyMetric", "")
            daily_values = []
            total = 0

            for point in series.get("dailyMetricTimeSeries", {}).get("dailySubEntityResults", []):
                value = int(point.get("value", 0))
                total += value
                daily_values.append({
                    "date": point.get("date", {}),
                    "value": value
                })

            # Aggregate into categories
            if "IMPRESSIONS" in metric_name:
                if "MAPS" in metric_name:
                    maps_views += total
                else:
                    search_views += total
            elif "CALL" in metric_name:
                phone_calls += total
            elif "WEBSITE" in metric_name:
                website_clicks += total
            elif "DIRECTION" in metric_name:
                direction_requests += total

            metrics_breakdown.append(GMBInsightsData(
                metric=metric_name,
                total_value=total,
                daily_values=daily_values
            ))

        total_views = maps_views + search_views

        return GMBInsightsResponse(
            location_name=location,
            period_start=start_date,
            period_end=end_date,
            total_searches=total_searches,
            direct_searches=0,
            discovery_searches=0,
            total_views=total_views,
            maps_views=maps_views,
            search_views=search_views,
            website_clicks=website_clicks,
            phone_calls=phone_calls,
            direction_requests=direction_requests,
            photo_views=0,
            metrics_breakdown=metrics_breakdown
        )

    async def get_full_dashboard(self, days: int = 30) -> GMBDashboardResponse:
        """Get complete GMB dashboard data."""
        import asyncio

        location, reviews, posts, insights = await asyncio.gather(
            self.get_location(),
            self.get_reviews(page_size=10),
            self.get_posts(page_size=10),
            self.get_insights(days=days),
            return_exceptions=True
        )

        # Handle exceptions
        if isinstance(location, Exception) or location is None:
            logger.error(f"Error getting location: {location}")
            location = GMBLocationInfo(name="", title="Unknown")
        if isinstance(reviews, Exception):
            logger.error(f"Error getting reviews: {reviews}")
            reviews = GMBReviewsResponse()
        if isinstance(posts, Exception):
            logger.error(f"Error getting posts: {posts}")
            posts = GMBPostsResponse()
        if isinstance(insights, Exception):
            logger.error(f"Error getting insights: {insights}")
            insights = GMBInsightsResponse(
                location_name="",
                period_start=date.today() - timedelta(days=days),
                period_end=date.today()
            )

        return GMBDashboardResponse(
            location=location,
            reviews=reviews,
            posts=posts,
            insights=insights,
            last_updated=datetime.utcnow()
        )
