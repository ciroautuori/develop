"""
Google Integration Schemas - Pydantic models
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


# ============================================================================
# GOOGLE ANALYTICS GA4 SCHEMAS
# ============================================================================

class GAMetricType(str, Enum):
    """GA4 Metric types."""
    ACTIVE_USERS = "activeUsers"
    NEW_USERS = "newUsers"
    SESSIONS = "sessions"
    SCREEN_PAGE_VIEWS = "screenPageViews"
    BOUNCE_RATE = "bounceRate"
    AVG_SESSION_DURATION = "averageSessionDuration"
    CONVERSIONS = "conversions"
    TOTAL_REVENUE = "totalRevenue"
    ENGAGED_SESSIONS = "engagedSessions"
    EVENT_COUNT = "eventCount"


class GADimensionType(str, Enum):
    """GA4 Dimension types."""
    DATE = "date"
    CITY = "city"
    COUNTRY = "country"
    DEVICE_CATEGORY = "deviceCategory"
    PAGE_PATH = "pagePath"
    SOURCE = "sessionSource"
    MEDIUM = "sessionMedium"
    CAMPAIGN = "sessionCampaignName"
    BROWSER = "browser"
    LANDING_PAGE = "landingPage"


class GADateRange(BaseModel):
    """Date range for GA4 queries."""
    start_date: str = Field(..., description="Start date (YYYY-MM-DD or relative like '30daysAgo')")
    end_date: str = Field(..., description="End date (YYYY-MM-DD or 'today')")


class GAReportRequest(BaseModel):
    """Request for GA4 report."""
    date_ranges: List[GADateRange] = Field(default_factory=lambda: [GADateRange(start_date="30daysAgo", end_date="today")])
    metrics: List[str] = Field(default_factory=lambda: ["activeUsers", "sessions", "screenPageViews"])
    dimensions: Optional[List[str]] = None
    order_by: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=10000)


class GAMetricValue(BaseModel):
    """Single metric value from GA4."""
    name: str
    value: str
    formatted_value: Optional[str] = None


class GADimensionValue(BaseModel):
    """Single dimension value from GA4."""
    name: str
    value: str


class GAReportRow(BaseModel):
    """Single row in GA4 report."""
    dimension_values: List[GADimensionValue] = Field(default_factory=list)
    metric_values: List[GAMetricValue]


class GAReportResponse(BaseModel):
    """Response from GA4 report."""
    rows: List[GAReportRow] = Field(default_factory=list)
    row_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GAOverviewMetrics(BaseModel):
    """Overview metrics for dashboard."""
    active_users: int = 0
    new_users: int = 0
    sessions: int = 0
    page_views: int = 0
    bounce_rate: float = 0.0
    avg_session_duration: float = 0.0
    conversions: int = 0
    period: str = "30d"


class GATrafficSource(BaseModel):
    """Traffic source data."""
    source: str
    medium: str
    users: int
    sessions: int
    percentage: float


class GATopPage(BaseModel):
    """Top page data."""
    path: str
    page_views: int
    unique_views: int
    avg_time_on_page: float


class GADeviceBreakdown(BaseModel):
    """Device breakdown data."""
    device: str  # desktop, mobile, tablet
    users: int
    sessions: int
    percentage: float


class GAGeographicData(BaseModel):
    """Geographic data."""
    country: str
    city: Optional[str] = None
    users: int
    sessions: int


class GADashboardResponse(BaseModel):
    """Complete GA4 dashboard data."""
    overview: GAOverviewMetrics
    traffic_sources: List[GATrafficSource] = Field(default_factory=list)
    top_pages: List[GATopPage] = Field(default_factory=list)
    device_breakdown: List[GADeviceBreakdown] = Field(default_factory=list)
    geographic_data: List[GAGeographicData] = Field(default_factory=list)
    daily_traffic: List[Dict[str, Any]] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# GOOGLE BUSINESS PROFILE SCHEMAS
# ============================================================================

class GMBLocationType(str, Enum):
    """GMB Location types."""
    STOREFRONT = "STOREFRONT"
    SERVICE_AREA = "SERVICE_AREA_BUSINESS"
    HYBRID = "HYBRID"


class GMBLocationInfo(BaseModel):
    """Google Business Profile location info."""
    name: str  # accounts/{accountId}/locations/{locationId}
    title: str
    store_code: Optional[str] = None
    address: Optional[Dict[str, str]] = None
    phone_number: Optional[str] = None
    website_uri: Optional[str] = None
    location_type: Optional[GMBLocationType] = None
    is_verified: bool = False


class GMBReviewRating(str, Enum):
    """Review rating values."""
    ONE = "ONE"
    TWO = "TWO"
    THREE = "THREE"
    FOUR = "FOUR"
    FIVE = "FIVE"


class GMBReview(BaseModel):
    """Google Business Profile review."""
    review_id: str
    reviewer_name: str
    reviewer_photo_url: Optional[str] = None
    star_rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None
    create_time: datetime
    update_time: Optional[datetime] = None
    reply: Optional[str] = None
    reply_time: Optional[datetime] = None


class GMBReviewsResponse(BaseModel):
    """Reviews list response."""
    reviews: List[GMBReview] = Field(default_factory=list)
    average_rating: float = 0.0
    total_reviews: int = 0
    next_page_token: Optional[str] = None


class GMBReviewReplyRequest(BaseModel):
    """Request to reply to a review."""
    review_id: str
    reply_text: str = Field(..., min_length=1, max_length=4096)


class GMBPostType(str, Enum):
    """GMB Post types."""
    STANDARD = "STANDARD"
    EVENT = "EVENT"
    OFFER = "OFFER"
    PRODUCT = "PRODUCT"


class GMBPostCallToAction(str, Enum):
    """Call to action types."""
    BOOK = "BOOK"
    ORDER = "ORDER"
    SHOP = "SHOP"
    LEARN_MORE = "LEARN_MORE"
    SIGN_UP = "SIGN_UP"
    CALL = "CALL"


class GMBPostCreate(BaseModel):
    """Create a GMB post."""
    summary: str = Field(..., min_length=1, max_length=1500)
    post_type: GMBPostType = GMBPostType.STANDARD
    media_urls: List[str] = Field(default_factory=list)
    call_to_action: Optional[GMBPostCallToAction] = None
    action_url: Optional[str] = None
    event_title: Optional[str] = None
    event_start: Optional[datetime] = None
    event_end: Optional[datetime] = None
    offer_code: Optional[str] = None
    offer_terms: Optional[str] = None


class GMBPost(BaseModel):
    """Google Business Profile post."""
    post_id: str
    summary: str
    post_type: GMBPostType
    create_time: datetime
    update_time: Optional[datetime] = None
    media_urls: List[str] = Field(default_factory=list)
    call_to_action: Optional[str] = None
    action_url: Optional[str] = None
    state: str = "LIVE"  # LIVE, REJECTED, PENDING
    view_count: int = 0
    click_count: int = 0


class GMBPostsResponse(BaseModel):
    """Posts list response."""
    posts: List[GMBPost] = Field(default_factory=list)
    total_posts: int = 0
    next_page_token: Optional[str] = None


class GMBInsightsMetric(str, Enum):
    """GMB Insights metrics."""
    QUERIES_DIRECT = "QUERIES_DIRECT"
    QUERIES_INDIRECT = "QUERIES_INDIRECT"
    QUERIES_CHAIN = "QUERIES_CHAIN"
    VIEWS_MAPS = "VIEWS_MAPS"
    VIEWS_SEARCH = "VIEWS_SEARCH"
    ACTIONS_WEBSITE = "ACTIONS_WEBSITE"
    ACTIONS_PHONE = "ACTIONS_PHONE"
    ACTIONS_DRIVING_DIRECTIONS = "ACTIONS_DRIVING_DIRECTIONS"
    PHOTOS_VIEWS_MERCHANT = "PHOTOS_VIEWS_MERCHANT"
    PHOTOS_VIEWS_CUSTOMERS = "PHOTOS_VIEWS_CUSTOMERS"


class GMBInsightsData(BaseModel):
    """Insights data for a period."""
    metric: str
    total_value: int
    daily_values: List[Dict[str, Any]] = Field(default_factory=list)


class GMBInsightsResponse(BaseModel):
    """Complete insights response."""
    location_name: str
    period_start: date
    period_end: date
    total_searches: int = 0
    direct_searches: int = 0
    discovery_searches: int = 0
    total_views: int = 0
    maps_views: int = 0
    search_views: int = 0
    website_clicks: int = 0
    phone_calls: int = 0
    direction_requests: int = 0
    photo_views: int = 0
    metrics_breakdown: List[GMBInsightsData] = Field(default_factory=list)


class GMBDashboardResponse(BaseModel):
    """Complete GMB dashboard data."""
    location: GMBLocationInfo
    reviews: GMBReviewsResponse
    posts: GMBPostsResponse
    insights: GMBInsightsResponse
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# OAUTH SCHEMAS
# ============================================================================

class GoogleOAuthScope(str, Enum):
    """Available Google OAuth scopes."""
    PROFILE = "https://www.googleapis.com/auth/userinfo.profile"
    EMAIL = "https://www.googleapis.com/auth/userinfo.email"
    OPENID = "openid"
    ANALYTICS_READONLY = "https://www.googleapis.com/auth/analytics.readonly"
    BUSINESS_MANAGE = "https://www.googleapis.com/auth/business.manage"
    SEARCH_CONSOLE = "https://www.googleapis.com/auth/webmasters.readonly"


class GoogleConnectionStatus(BaseModel):
    """Status of Google integration connection."""
    analytics_connected: bool = False
    business_profile_connected: bool = False
    search_console_connected: bool = False
    analytics_property_id: Optional[str] = None
    business_account_id: Optional[str] = None
    business_location_id: Optional[str] = None
    last_sync: Optional[datetime] = None
    token_expires_at: Optional[datetime] = None


class GoogleConnectRequest(BaseModel):
    """Request to initiate Google OAuth."""
    scopes: List[str] = Field(
        default_factory=lambda: [
            "openid",
            "email",
            "profile",
            "https://www.googleapis.com/auth/analytics.readonly",
            "https://www.googleapis.com/auth/business.manage"
        ]
    )
    redirect_uri: Optional[str] = None


class GooglePropertySelect(BaseModel):
    """Select GA4 property or GMB location."""
    property_id: Optional[str] = None  # GA4 property ID
    account_id: Optional[str] = None  # GMB account ID
    location_id: Optional[str] = None  # GMB location ID
