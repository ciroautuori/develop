"""
Core Configuration
Centralized configuration using Pydantic Settings
"""

from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings - loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Service Configuration
    AI_SERVICE_HOST: str = Field(default="0.0.0.0", description="Service host")
    AI_SERVICE_PORT: int = Field(default=8001, description="Service port")
    AI_SERVICE_API_KEY: str = Field(
        default="dev-api-key-change-in-production",
        description="API key for authentication"
    )
    AI_SERVICE_ENV: str = Field(default="development", description="Environment")

    # AI Providers (Priority: GROQ [FREE!] → HuggingFace → Gemini → OpenRouter)
    # GROQ is FREE and FAST with 5 API keys for rate limiting!
    GROQ_API_KEY: str = Field(default="", description="GROQ API key (Primary - FREE)")
    GROQ_API_KEY_2: str = Field(default="", description="GROQ API key backup 2")
    GROQ_API_KEY_3: str = Field(default="", description="GROQ API key backup 3")
    GROQ_API_KEY_4: str = Field(default="", description="GROQ API key backup 4")
    GROQ_API_KEY_5: str = Field(default="", description="GROQ API key backup 5")

    # Support both GOOGLE_AI_API_KEY and GOOGLE_API_KEY for backward compatibility
    GOOGLE_AI_API_KEY: str = Field(default="", description="Google Gemini API key")
    GOOGLE_API_KEY: str = Field(default="", description="Google API key (Alias)")
    OPENROUTER_API_KEY: str = Field(default="", description="OpenRouter API key (Pay-per-use)")
    HUGGINGFACE_API_KEY: str = Field(default="", description="HuggingFace API key")
    HUGGINGFACE_TOKEN: str = Field(default="", description="HuggingFace token (Alias)")

    # Custom Model Configuration
    USE_CUSTOM_MODEL: bool = Field(
        default=True,
        description="Use custom StudioCentOS model instead of Gemini"
    )
    HUGGINGFACE_MODEL_NAME: str = Field(
        default="autuoriciro/studiocentos-ai-qwen-3b",
        description="Custom model name on HuggingFace"
    )

    OLLAMA_HOST: str = Field(
        default="central-ollama",
        description="Ollama host (PRIMARY LLM provider)"
    )
    OLLAMA_PORT: int = Field(
        default=11434,
        description="Ollama port"
    )
    OLLAMA_MODEL: str = Field(
        default="llama3.2:latest",
        description="Ollama model to use"
    )
    OLLAMA_BASE_URL: str = Field(
        default="http://central-ollama:11434",
        description="Ollama base URL (constructed from host:port)"
    )

    # ChromaDB Configuration
    CHROMADB_HOST: str = Field(default="localhost", description="ChromaDB host")
    CHROMADB_PORT: int = Field(default=8000, description="ChromaDB port")
    CHROMADB_PERSIST_DIR: str = Field(
        default="/data/chromadb",
        description="ChromaDB persistence directory"
    )
    CHROMADB_TOKEN: str = Field(default="", description="ChromaDB authentication token")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit per minute")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, description="Rate limit per hour")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format")

    # CORS Configuration
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Allowed CORS origins (comma-separated)"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, description="Enable Prometheus metrics")
    METRICS_PORT: int = Field(default=9090, description="Metrics port")

    # RAG Configuration
    RAG_CHUNK_SIZE: int = Field(default=500, description="RAG chunk size")
    RAG_CHUNK_OVERLAP: int = Field(default=50, description="RAG chunk overlap")
    RAG_SIMILARITY_THRESHOLD: float = Field(
        default=0.7,
        description="RAG similarity threshold"
    )
    RAG_MAX_RESULTS: int = Field(default=5, description="RAG max results")

    # =========================================================================
    # SOCIAL MEDIA API CREDENTIALS
    # =========================================================================

    # Twitter/X API
    TWITTER_CLIENT_ID: str = Field(default="", description="Twitter OAuth 2.0 Client ID")
    TWITTER_CLIENT_SECRET: str = Field(default="", description="Twitter OAuth 2.0 Client Secret")
    TWITTER_API_KEY: str = Field(default="", description="Twitter API Key (OAuth 1.0a)")
    TWITTER_API_SECRET: str = Field(default="", description="Twitter API Secret")
    TWITTER_ACCESS_TOKEN: str = Field(default="", description="Twitter Access Token")
    TWITTER_ACCESS_TOKEN_SECRET: str = Field(default="", description="Twitter Access Token Secret")
    TWITTER_REFRESH_TOKEN: str = Field(default="", description="Twitter OAuth 2.0 Refresh Token")

    # Facebook API
    FACEBOOK_APP_ID: str = Field(default="", description="Facebook App ID")
    FACEBOOK_APP_SECRET: str = Field(default="", description="Facebook App Secret")
    FACEBOOK_PAGE_ID: str = Field(default="", description="Facebook Page ID")
    FACEBOOK_PAGE_ACCESS_TOKEN: str = Field(default="", description="Facebook Page Access Token")

    # LinkedIn API
    LINKEDIN_CLIENT_ID: str = Field(default="", description="LinkedIn Client ID")
    LINKEDIN_CLIENT_SECRET: str = Field(default="", description="LinkedIn Client Secret")
    LINKEDIN_ACCESS_TOKEN: str = Field(default="", description="LinkedIn Access Token")
    LINKEDIN_REFRESH_TOKEN: str = Field(default="", description="LinkedIn Refresh Token")
    LINKEDIN_ORGANIZATION_ID: str = Field(default="", description="LinkedIn Organization/Company ID")

    # Instagram API (via Facebook)
    INSTAGRAM_BUSINESS_ID: str = Field(default="", description="Instagram Business Account ID")

    # =========================================================================
    # SEO & ANALYTICS API CREDENTIALS
    # =========================================================================

    # Google APIs
    GOOGLE_CREDENTIALS_JSON: str = Field(default="", description="Google Service Account JSON (can be path or JSON string)")
    GOOGLE_SEARCH_CONSOLE_CREDENTIALS: str = Field(default="", description="Google Search Console JSON credentials")
    GOOGLE_SEARCH_CONSOLE_SITE: str = Field(default="", description="Google Search Console Site URL (e.g., https://example.com/)")
    GA4_PROPERTY_ID: str = Field(default="", description="Google Analytics 4 Property ID (numeric)")
    GA4_CREDENTIALS: str = Field(default="", description="GA4 Service Account JSON credentials")

    # SEO Tools
    SEMRUSH_API_KEY: str = Field(default="", description="SEMrush API Key")
    AHREFS_API_KEY: str = Field(default="", description="Ahrefs API Key")
    MOZ_API_KEY: str = Field(default="", description="Moz API Key")

    # Email Marketing
    SENDGRID_API_KEY: str = Field(default="", description="SendGrid API Key")
    SENDGRID_FROM_EMAIL: str = Field(default="noreply@studiocentos.it", description="SendGrid sender email")
    SENDGRID_FROM_NAME: str = Field(default="StudioCentos", description="SendGrid sender name")
    MAILCHIMP_API_KEY: str = Field(default="", description="Mailchimp API Key")
    MAILCHIMP_LIST_ID: str = Field(default="", description="Mailchimp default audience ID")

    # Lead Intelligence
    APOLLO_API_KEY: str = Field(default="", description="Apollo.io API Key")
    ZOOMINFO_API_KEY: str = Field(default="", description="ZoomInfo API Key")
    CLEARBIT_API_KEY: str = Field(default="", description="Clearbit API Key")
    HUNTER_API_KEY: str = Field(default="", description="Hunter.io API Key")

    # Payment/Stripe
    STRIPE_API_KEY: str = Field(default="", description="Stripe Secret Key")
    STRIPE_WEBHOOK_SECRET: str = Field(default="", description="Stripe Webhook Secret")

    # WhatsApp Business
    WHATSAPP_ACCESS_TOKEN: str = Field(default="", description="WhatsApp Cloud API Access Token")
    WHATSAPP_PHONE_NUMBER_ID: str = Field(default="", description="WhatsApp Phone Number ID")
    WHATSAPP_BUSINESS_ID: str = Field(default="", description="WhatsApp Business Account ID")

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.AI_SERVICE_ENV == "production"

    @property
    def chromadb_url(self) -> str:
        """Get ChromaDB URL"""
        return f"http://{self.CHROMADB_HOST}:{self.CHROMADB_PORT}"

    @property
    def groq_api_keys(self) -> list:
        """Get all GROQ API keys for rotation/fallback"""
        keys = [
            self.GROQ_API_KEY,
            self.GROQ_API_KEY_2,
            self.GROQ_API_KEY_3,
            self.GROQ_API_KEY_4,
            self.GROQ_API_KEY_5,
        ]
        return [k for k in keys if k]  # Filter empty keys

    @property
    def google_api_key_resolved(self) -> str:
        """Get Google API key with fallback"""
        return self.GOOGLE_AI_API_KEY or self.GOOGLE_API_KEY

    @property
    def huggingface_token_resolved(self) -> str:
        """Get HuggingFace token with fallback"""
        return self.HUGGINGFACE_TOKEN or self.HUGGINGFACE_API_KEY


# Global settings instance
settings = Settings()
