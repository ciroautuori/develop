from pydantic_settings import BaseSettings
from pydantic import Field
import os
from typing import List


class Settings(BaseSettings):
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres@localhost/iss_wbs",
        alias="DATABASE_URL"
    )
    # SQLAlchemy engine tuning
    sqlalchemy_echo: bool = Field(default=False, alias="SQLALCHEMY_ECHO")
    db_pool_size: int = Field(default=5, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(default=30, alias="DB_POOL_TIMEOUT")
    db_pool_recycle: int = Field(default=1800, alias="DB_POOL_RECYCLE")

    # JWT Security
    secret_key: str = Field(
        default="your-secret-key-here-change-in-production",
        alias="SECRET_KEY"
    )
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # API Settings
    api_v1_prefix: str = "/api/v1"
    project_name: str = "ISS WBS API"
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # CORS
    allowed_origins_str: str = Field(
        default="http://localhost:3000,https://localhost:3000,http://localhost:3001,https://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001",
        alias="ALLOWED_ORIGINS"
    )

    @property
    def origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins_str.split(',')]

    # Redis for rate limiting
    redis_url: str = Field(
        default="redis://localhost:6379",
        alias="REDIS_URL"
    )

    # Security
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15

    # Media upload
    upload_dir: str = Field(default="./static/uploads", alias="UPLOAD_DIR")
    max_file_size_mb: int = 10
    allowed_file_types: List[str] = [
        "image/jpeg", "image/png", "image/webp", "image/gif",
        "application/pdf", "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]

    # Email settings
    mail_username: str = Field(default="", alias="MAIL_USERNAME")
    mail_password: str = Field(default="", alias="MAIL_PASSWORD")
    mail_from: str = Field(default="noreply@iss-aps.it", alias="MAIL_FROM")
    mail_port: int = Field(default=587, alias="MAIL_PORT")
    mail_server: str = Field(default="smtp.gmail.com", alias="MAIL_SERVER")
    mail_starttls: bool = Field(default=True, alias="MAIL_STARTTLS")
    mail_ssl_tls: bool = Field(default=False, alias="MAIL_SSL_TLS")

    # Stripe/Payment
    stripe_public_key: str = Field(default="", alias="STRIPE_PUBLIC_KEY")
    stripe_secret_key: str = Field(default="", alias="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str = Field(default="", alias="STRIPE_WEBHOOK_SECRET")

    # Observability
    sentry_dsn: str = Field(default="", alias="SENTRY_DSN")

    # Caching
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")

    # AI Services for Bandi Search
    google_api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    huggingface_token: str = Field(default="", alias="HUGGINGFACE_TOKEN")
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")

    # AI Search Settings
    ai_search_enabled: bool = Field(default=True, alias="AI_SEARCH_ENABLED")
    ai_model: str = Field(default="gemini-2.0-flash", alias="AI_MODEL")

    # Ollama Settings
    ollama_host: str = Field(default="central-ollama", alias="OLLAMA_HOST")
    ollama_port: int = Field(default=11434, alias="OLLAMA_PORT")
    ollama_model: str = Field(default="llama3.2:latest", alias="OLLAMA_MODEL")
    use_ollama: bool = Field(default=True, alias="USE_OLLAMA")
    llm_provider: str = Field(default="ollama", alias="LLM_PROVIDER")

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }


settings = Settings()
