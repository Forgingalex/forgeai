"""
Application configuration.

Uses Pydantic Settings for environment variable management.
Supports .env file and environment variables.
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""
    
    # App
    APP_NAME: str = "ForgeAI"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg://forgeai:forgeai@localhost/forgeai"
    DATABASE_URL_ASYNC: str = "postgresql+asyncpg://forgeai:forgeai@localhost/forgeai"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]
    
    # AI APIs - Ollama (Free, Local, Unlimited, Fallback)
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "llama3.1:8b")
    
    # Google AI Studio (Gemini API) - Fast, cloud-based, Primary provider
    GOOGLE_AI_API_KEY: str = os.getenv("GOOGLE_AI_API_KEY", "")
    GOOGLE_AI_MODEL: str = os.getenv("GOOGLE_AI_MODEL", "gemini-2.5-flash")  # Fast, latest flash model
    
    # Legacy (optional fallback - not used with Ollama)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # File Storage
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

