import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # App
    APP_NAME: str = "ForgeAI"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # Database; Reading from environment (Neon)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://forgeai:forgeai@localhost/forgeai")
    DATABASE_URL_ASYNC: str = os.getenv("DATABASE_URL_ASYNC", "postgresql+asyncpg://forgeai:forgeai@localhost/forgeai")
    
    # Redis; master source
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Celery; point to REDIS_URL and not be redefined below
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL
    CELERY_TASK_ALWAYS_EAGER: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"] # Tip: Allowed for initial cloud test
    
    # AI APIs
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")
    
    GOOGLE_AI_API_KEY: str = os.getenv("GOOGLE_AI_API_KEY", "")
    GOOGLE_AI_MODEL: str = os.getenv("GOOGLE_AI_MODEL", "gemini-1.5-flash")

    # Vector search
    CHROMA_MODE: str = os.getenv("CHROMA_MODE", "persistent")
    CHROMA_PERSIST_DIR: Path = Path(os.getenv("CHROMA_PERSIST_DIR", "chroma_data"))
    CHROMA_COLLECTION: str = os.getenv("CHROMA_COLLECTION", "forgeai_knowledge")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

    # File Storage
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
if settings.CHROMA_MODE == "persistent":
    settings.CHROMA_PERSIST_DIR.mkdir(parents=True, exist_ok=True)