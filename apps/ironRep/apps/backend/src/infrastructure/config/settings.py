"""
Settings and Configuration
"""
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM API Keys
    groq_api_key: str
    openrouter_api_key: str
    google_api_key: str
    huggingface_api_key: Optional[str] = None

    # Google OAuth (Calendar, YouTube)
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    google_redirect_uri: str = "http://localhost:8000/api/google/auth/callback"
    youtube_api_key: Optional[str] = None

    # LLM Configuration
    primary_llm_model: str = "llama-3.3-70b-versatile"
    gemini_model: str = "gemini-2.0-flash"
    fallback_models: str = "meta-llama/llama-3.2-3b-instruct:free,google/gemma-2-9b-it:free"

    # Database
    database_url: str = "postgresql://ironrep:ironrep@localhost:5432/ironrep"

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8000

    # Application
    debug: bool = True
    log_level: str = "INFO"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_port: int = 8501
    
    # Paths
    data_dir: str = "/app/data"

    # CORS
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost",
        "https://ironrep.it",
        "https://www.ironrep.it",
        "https://ironrep.eu",
        "https://www.ironrep.eu"
    ]

    # Authentication
    secret_key: str = "dev-only-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_fallback_models_list(self) -> List[str]:
        return [m.strip() for m in self.fallback_models.split(",")]

    def get_groq_api_keys_list(self) -> List[str]:
        return [k.strip() for k in self.groq_api_key.split(",")]


settings = Settings()
