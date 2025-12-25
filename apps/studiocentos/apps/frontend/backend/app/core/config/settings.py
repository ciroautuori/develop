import logging
import os
import secrets
from typing import Optional

from dotenv import load_dotenv
from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings

# Carica le variabili di ambiente dal file .env
load_dotenv()

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", case_sensitive=True)

    # Environment
    ENVIRONMENT: str = Field(default="development")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # API settings
    API_PREFIX: str = os.getenv("API_PREFIX", "/api")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Static files
    STATIC_FILES_DIR: str = os.getenv("STATIC_FILES_DIR", "app/static")

    # Application settings
    APP_NAME: str = os.getenv("APP_NAME", "StudioCentOS")
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "StudioCentOS Portfolio API")
    VERSION: str = os.getenv("VERSION", "2.1.0")
    ENABLE_RATE_LIMITING: bool = os.getenv("ENABLE_RATE_LIMITING", "True").lower() == "true"

    # Security - CRITICAL FIX: No auto-generation in production
    SECRET_KEY: str = Field(default="")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))  # 7 days default

    # Database settings
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_USER: str = os.getenv("DB_USER", "cvlab")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")  # Required in production
    DB_NAME: str = os.getenv("DB_NAME", "cvlab_portfolio")

    # Redis settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # SMTP settings (required in production for notifications)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")  # Required if email enabled
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")  # Required if email enabled
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "true").lower() == "true"

    # Email settings
    EMAILS_FROM_EMAIL: str = os.getenv("EMAILS_FROM_EMAIL", "noreply@studiocentos.it")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "StudioCentOS")

    # External services
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Admin settings

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Valida SECRET_KEY con regole strict per produzione.
        CRITICAL SECURITY: Previene auto-generation che invalida JWT.
        """
        environment = os.getenv("ENVIRONMENT", "development")

        if environment == "production":
            if not v or len(v) < 32:
                raise ValueError(
                    "❌ CRITICAL SECURITY: SECRET_KEY must be explicitly set in production "
                    "and be at least 32 characters long. "
                    "Generate with: openssl rand -hex 32"
                )
        else:
            # Development: Warn se non impostata ma allow auto-generation
            if not v:
                import secrets

                v = secrets.token_urlsafe(32)
                print("⚠️  WARNING: SECRET_KEY not set, auto-generated for development only")
                print(f"    Generated: {v[:16]}...")
                print("    Set SECRET_KEY in .env for consistent JWT tokens")

        return v

    @field_validator("DB_PASSWORD")
    @classmethod
    def validate_db_password(cls, v: str, info) -> str:
        """Valida DB_PASSWORD - required in production.
        CRITICAL SECURITY: Database credentials must be explicitly set.
        """
        environment = os.getenv("ENVIRONMENT", "development")

        if environment == "production":
            if not v:
                raise ValueError(
                    "❌ CRITICAL SECURITY: DB_PASSWORD must be explicitly set in production. "
                    "Never use default credentials in production environment."
                )
        else:
            # Development: Warn if not set
            if not v:
                print("⚠️  WARNING: DB_PASSWORD not set in development")
                print("    Using empty password - ensure database allows this")

        return v

    # Admin
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")

    # Frontend App URL (for OAuth redirects)
    FRONTEND_APP_URL: str = os.getenv("FRONTEND_APP_URL", "http://localhost:8080")

    # Base URLs for different environments
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:8080")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")

    # Billing URLs
    BILLING_SUCCESS_URL: str = os.getenv("BILLING_SUCCESS_URL", "")
    BILLING_CANCEL_URL: str = os.getenv("BILLING_CANCEL_URL", "")

    # Portfolio/QR Code base URL
    PORTFOLIO_BASE_URL: str = os.getenv("PORTFOLIO_BASE_URL", "")

    # Password reset URL base
    PASSWORD_RESET_BASE_URL: str = os.getenv("PASSWORD_RESET_BASE_URL", "")

    @property
    def BILLING_SUCCESS_URL_COMPUTED(self) -> str:
        """Get billing success URL with fallback to frontend URL."""
        return self.BILLING_SUCCESS_URL or f"{self.FRONTEND_URL}/billing/success"

    @property
    def BILLING_CANCEL_URL_COMPUTED(self) -> str:
        """Get billing cancel URL with fallback to frontend URL."""
        return self.BILLING_CANCEL_URL or f"{self.FRONTEND_URL}/billing/cancel"

    @property
    def PASSWORD_RESET_URL_BASE_COMPUTED(self) -> str:
        """Get password reset URL base with fallback."""
        return self.PASSWORD_RESET_BASE_URL or f"{self.FRONTEND_URL}/auth/reset-password"

    @property
    def PORTFOLIO_BASE_URL_COMPUTED(self) -> str:
        """Get portfolio base URL with fallback."""
        return self.PORTFOLIO_BASE_URL or f"{self.FRONTEND_URL}/portfolio"

    # Stripe Configuration - SECURITY: Empty defaults to prevent test key leakage
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_PUBLISHABLE_KEY: str = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    STRIPE_PRICE_ID_MONTHLY: str = os.getenv("STRIPE_PRICE_ID_MONTHLY", "")
    STRIPE_PRICE_ID_YEARLY: str = os.getenv("STRIPE_PRICE_ID_YEARLY", "")

    # Feature Flag: Allow test keys in staging environments
    ALLOW_STRIPE_TEST_KEYS: bool = Field(
        default=False,
        description="Allow Stripe test keys in production mode (staging environments only)"
    )

    # LinkedIn OAuth
    LINKEDIN_CLIENT_ID: str = os.getenv("LINKEDIN_CLIENT_ID", "")
    LINKEDIN_CLIENT_SECRET: str = os.getenv("LINKEDIN_CLIENT_SECRET", "")
    LINKEDIN_REDIRECT_URI: str = os.getenv("LINKEDIN_REDIRECT_URI", "")

    @property
    def LINKEDIN_REDIRECT_URI_COMPUTED(self) -> str:
        """Get LinkedIn redirect URI with fallback."""
        return self.LINKEDIN_REDIRECT_URI or f"{self.FRONTEND_URL}/api/v1/auth/linkedin/callback"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "")

    @property
    def GOOGLE_REDIRECT_URI_COMPUTED(self) -> str:
        """Get Google redirect URI with fallback."""
        return self.GOOGLE_REDIRECT_URI or f"{self.FRONTEND_URL}/api/v1/auth/google/callback"

    # Google Analytics & Business Profile
    GA4_PROPERTY_ID: str = Field(default="properties/467399370", description="Google Analytics 4 Property ID")
    GMB_ACCOUNT_ID: str = Field(default="", description="Google Business Profile Account ID")
    GMB_LOCATION_ID: str = Field(default="", description="Google Business Profile Location ID")

    # Base URL for callbacks
    BASE_URL: str = os.getenv("BASE_URL", "https://studiocentos.it")

    # AI Support Settings
    OPENAI_API_KEY: str = Field(default="")
    GOOGLE_AI_API_KEY: str = Field(default="")
    HUGGINGFACE_API_KEY: str = Field(default="")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    OPENROUTER_API_KEY: str = Field(default="", description="OpenRouter API key for embeddings fallback")

    # Google Cloud / Vertex AI (for Veo Video Generation)
    GOOGLE_CLOUD_PROJECT: str = Field(default="", description="Google Cloud Project ID")
    GOOGLE_CLOUD_REGION: str = Field(default="us-central1", description="Google Cloud Region")
    GOOGLE_API_KEY: str = Field(default="", description="Google API Key for Vertex AI")

    # =============================================================================
    # SOCIAL MEDIA API CREDENTIALS
    # =============================================================================

    # Meta/Facebook App
    META_APP_ID: str = Field(default="", description="Meta/Facebook App ID")
    META_APP_SECRET: str = Field(default="", description="Meta/Facebook App Secret")
    META_ACCESS_TOKEN: str = Field(default="", description="Meta/Facebook long-lived access token")
    FACEBOOK_PAGE_ID: str = Field(default="", description="Facebook Page ID for posting")

    # Threads App
    THREADS_APP_ID: str = Field(default="", description="Threads App ID")
    THREADS_APP_SECRET: str = Field(default="", description="Threads App Secret")
    THREADS_ACCESS_TOKEN: str = Field(default="", description="Threads long-lived access token")
    THREADS_USER_ID: str = Field(default="", description="Threads User ID for posting")

    # Twitter/X (Legacy from existing integration)
    TWITTER_API_KEY: str = Field(default="", description="Twitter API Key")
    TWITTER_API_SECRET: str = Field(default="", description="Twitter API Secret")
    TWITTER_ACCESS_TOKEN: str = Field(default="", description="Twitter Access Token")
    TWITTER_ACCESS_SECRET: str = Field(default="", description="Twitter Access Secret")
    TWITTER_BEARER_TOKEN: str = Field(default="", description="Twitter Bearer Token")

    # LinkedIn (already exists via OAuth but add posting token)
    LINKEDIN_ACCESS_TOKEN: str = Field(default="", description="LinkedIn Access Token for API posting")

    # Instagram Business Account
    INSTAGRAM_ACCOUNT_ID: str = Field(default="", description="Instagram Business Account ID")
    INSTAGRAM_ACCESS_TOKEN: str = Field(default="", description="Instagram Access Token")

    # WhatsApp Cloud API (uses Meta Graph API)
    WHATSAPP_PHONE_NUMBER_ID: str = Field(default="", description="WhatsApp Business Phone Number ID")
    WHATSAPP_ACCESS_TOKEN: str = Field(default="", description="WhatsApp Cloud API Access Token")
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = Field(default="", description="WhatsApp Business Account ID")
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = Field(default="", description="Webhook verification token")
    WHATSAPP_API_VERSION: str = Field(default="v21.0", description="Meta Graph API version")

    # CORS - Environment-based configuration
    @property
    def BACKEND_CORS_ORIGINS(self) -> list[str]:
        """CORS origins basati su environment.
        SECURITY FIX: Previene localhost leakage in produzione.
        """
        if self.ENVIRONMENT == "production":
            return [
                "https://cv-lab.pro", "https://www.cv-lab.pro", "https://app.cv-lab.pro",
                "https://studiocentos.it", "https://www.studiocentos.it", "https://app.studiocentos.it",
                "https://play.google.com", "https://accounts.google.com"
            ]
        else:
            # Development/Staging
            return [
                "http://localhost",  # Nginx frontend (porta 80)
                "http://localhost:80",  # Nginx frontend (porta 80 esplicita)
                "http://localhost:3000",
                "http://localhost:5173",
                "http://localhost:5174",
                "http://localhost:8000",
                "http://localhost:8080",
                "http://127.0.0.1",  # Nginx frontend (porta 80)
                "http://127.0.0.1:80",  # Nginx frontend (porta 80 esplicita)
                "http://127.0.0.1:5173",
                "http://127.0.0.1:5174",
                "http://frontend:3000",
                "http://frontend:5173",
                # Google OAuth domains (per development)
                "https://accounts.google.com",
                "https://play.google.com",
            ]

    # Alias for backward compatibility
    CORS_ORIGINS: list[str] = []  # Populated by property

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Check if SECRET_KEY was auto-generated
        if not os.getenv("SECRET_KEY"):
            logging.warning(
                "No SECRET_KEY in environment. Generated temporary key for development."
            )

        self._validate_production_secrets()

    def _validate_production_secrets(self):
        """Validate that production secrets are secure."""
        environment = os.getenv("ENVIRONMENT", "development")

        if environment == "production":
            # Check for development secrets in production
            if "dev-" in self.SECRET_KEY.lower():
                raise ValueError("❌ SECURITY: Development SECRET_KEY detected in production!")

            if "dev-" in self.ADMIN_PASSWORD.lower() or self.ADMIN_PASSWORD == "admin123":
                raise ValueError("❌ SECURITY: Weak ADMIN_PASSWORD detected in production!")

            if len(self.SECRET_KEY) < 32:
                raise ValueError("❌ SECURITY: SECRET_KEY too short for production (min 32 chars)!")

            # Validate Stripe keys in production with feature flag (OPTIONAL)
            # Skip validation if Stripe keys are not configured
            if self.STRIPE_SECRET_KEY or self.STRIPE_PUBLISHABLE_KEY:
                if not self.ALLOW_STRIPE_TEST_KEYS:
                    # Strict validation for production
                    if self.STRIPE_SECRET_KEY and self.STRIPE_SECRET_KEY.startswith("sk_test_"):
                        raise ValueError(
                            "❌ SECURITY: Production requires LIVE Stripe secret key (sk_live_...). "
                            "Test keys (sk_test_...) are not allowed in production. "
                            "Set ALLOW_STRIPE_TEST_KEYS=true ONLY for staging environments."
                        )

                    if self.STRIPE_PUBLISHABLE_KEY and self.STRIPE_PUBLISHABLE_KEY.startswith("pk_test_"):
                        raise ValueError(
                            "❌ SECURITY: Production requires LIVE Stripe publishable key (pk_live_...). "
                            "Test keys (pk_test_...) are not allowed in production."
                        )

                    if self.STRIPE_SECRET_KEY and self.STRIPE_PUBLISHABLE_KEY:
                        logging.info("✅ Stripe keys validation passed (LIVE keys)")
                else:
                    # Feature flag enabled - allowing test keys for staging
                    logging.warning("⚠️ SECURITY WARNING: ALLOW_STRIPE_TEST_KEYS=true detected!")
                    logging.warning("   Stripe test keys are allowed in production mode.")
                    logging.warning("   This should ONLY be used for staging environments.")

                    if self.STRIPE_SECRET_KEY and self.STRIPE_SECRET_KEY.startswith("sk_test_"):
                        logging.info("   Using Stripe TEST secret key (staging mode)")
                    elif self.STRIPE_SECRET_KEY and self.STRIPE_SECRET_KEY.startswith("sk_live_"):
                        logging.info("   Using Stripe LIVE secret key")
            else:
                logging.info("ℹ️ Stripe not configured - billing features disabled")

        logging.info(f"✅ SECURITY: Environment '{environment}' secrets validation passed")

    # =============================================================================
    # ENRICHMENT SETTINGS - FREE TIER API INTEGRATION
    # =============================================================================

    # Feature toggles
    ENABLE_ENRICHMENT: bool = Field(default=True, description="Enable data enrichment features")
    ENABLE_COMPANY_ENRICHMENT: bool = Field(
        default=True, description="Enable company logo/data enrichment"
    )
    ENABLE_UNIVERSITY_ENRICHMENT: bool = Field(
        default=True, description="Enable university data enrichment"
    )

    # Cache settings
    ENRICHMENT_CACHE_TTL_COMPANY: int = Field(default=86400, description="Company cache TTL (24h)")
    ENRICHMENT_CACHE_TTL_UNIVERSITY: int = Field(
        default=604800, description="University cache TTL (7d)"
    )

    # API limits and timeouts
    ENRICHMENT_REQUEST_TIMEOUT: int = Field(default=5, description="API request timeout (seconds)")
    ENRICHMENT_MAX_CONCURRENT: int = Field(
        default=5, description="Max concurrent enrichment requests"
    )
    ENRICHMENT_MAX_BULK_SIZE: int = Field(default=50, description="Max items per bulk request")

    # External API endpoints
    CLEARBIT_LOGO_URL: str = Field(
        default="https://logo.clearbit.com", description="Clearbit Logo API base URL"
    )
    HIPOLABS_API_URL: str = Field(
        default="http://universities.hipolabs.com/search", description="Hipolabs Universities API"
    )

    # Future paid tier (when needed)
    CLEARBIT_API_KEY: Optional[str] = Field(
        default=None, description="Clearbit API key for paid features"
    )
    BRANDFETCH_API_KEY: Optional[str] = Field(
        default=None, description="Brandfetch API key for paid features"
    )

    def model_post_init(self, __context):
        """Post-init per costruire DATABASE_URL se non fornita."""
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

        # Auto-genera SECRET_KEY solo in development se non fornita
        if not self.SECRET_KEY and self.ENVIRONMENT == "development":
            self.SECRET_KEY = secrets.token_urlsafe(32)
            logging.warning("⚠️ SECRET_KEY auto-generated for development (will change on restart)")

    def get_configuration_summary(self) -> dict:
        """Restituisce un summary della configurazione (con secrets mascherati)."""
        return {
            "PROJECT_NAME": self.PROJECT_NAME,
            "VERSION": self.VERSION,
            "ENVIRONMENT": self.ENVIRONMENT,
            "DEBUG": self.DEBUG,
            "DATABASE_URL": self._mask_url(self.DATABASE_URL),
            "REDIS_URL": self._mask_url(self.REDIS_URL),
            "SECRET_KEY": "***" if self.SECRET_KEY else "NOT_SET",
            "ALGORITHM": self.ALGORITHM,
            "LOG_LEVEL": self.LOG_LEVEL,
            "ENABLE_RATE_LIMITING": self.ENABLE_RATE_LIMITING,
        }

    def is_development_setup(self) -> bool:
        """Verifica se il setup è per development."""
        return self.ENVIRONMENT == "development" and self.DEBUG

    def is_production_ready(self) -> bool:
        """Verifica se il setup è pronto per production."""
        if self.ENVIRONMENT != "production":
            return False
        return len(self.SECRET_KEY) >= 32 and self.DATABASE_URL and not self.DEBUG

    def _mask_url(self, url: str) -> str:
        """Maschera le credenziali nelle URL."""
        if "://" not in url:
            return url
        try:
            parts = url.split("://")
            if len(parts) == 2:
                protocol, rest = parts
                if "@" in rest:
                    credentials, host_path = rest.split("@", 1)
                    return f"{protocol}://***@{host_path}"
            return url
        except:
            return "***"

# Istanza delle impostazioni da usare in tutta l'app
settings = Settings()
