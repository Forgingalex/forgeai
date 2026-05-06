import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings


"""Application configuration."""


class Settings(BaseSettings):
    """Application settings."""
    
    # App
    APP_NAME: str = "ForgeAI"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg://forgeai:forgeai@localhost/forgeai"
    DATABASE_URL_ASYNC: str = "postgresql+asyncpg://forgeai:forgeai@localhost/forgeai"
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Ensure Celery variables also point to the master REDIS_URL
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]
    
    # AI APIs - Ollama (local fallback) and Google Gemini (primary).
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "llama3.1:8b")

    # Google AI Studio (Gemini API).
    GOOGLE_AI_API_KEY: str = os.getenv("GOOGLE_AI_API_KEY", "")
    GOOGLE_AI_MODEL: str = os.getenv("GOOGLE_AI_MODEL", "gemini-1.5-pro")

    # Legacy optional providers.
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Vector search.
    CHROMA_MODE: str = os.getenv("CHROMA_MODE", "persistent")
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8001"))
    CHROMA_PERSIST_DIR: Path = Path(os.getenv("CHROMA_PERSIST_DIR", "chroma_data"))
    CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "forgeai_knowledge")
    EMBEDDING_MODEL_NAME: str = os.getenv(
        "EMBEDDING_MODEL_NAME",
        "sentence-transformers/all-MiniLM-L6-v2",
    )
    HYBRID_SEMANTIC_WEIGHT: float = float(os.getenv("HYBRID_SEMANTIC_WEIGHT", "0.72"))

    # File Storage
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB

    # Celery.
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    CELERY_TASK_ALWAYS_EAGER: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Ensure upload directory exists
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
if settings.CHROMA_MODE == "persistent":
    settings.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)
