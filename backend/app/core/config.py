import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Production-grade application configuration."""
    APP_NAME: str = "ForgeAI"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "25ba0d6151d1a38c6e185c8f843b19f800019be2d36454ce0c28e1f8ff771551")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+psycopg://forgeai:forgeai@localhost/forgeai")
    
    # Redis & Celery
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = REDIS_URL
    CELERY_RESULT_BACKEND: str = REDIS_URL
    CELERY_TASK_ALWAYS_EAGER: bool = False
    
    # CORS - prevent JSON parsing errors in cloud
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    
    # AI APIs
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:1.5b")
    GOOGLE_AI_API_KEY: str = os.getenv("GOOGLE_AI_API_KEY", "")
    GOOGLE_AI_MODEL: str = os.getenv("GOOGLE_AI_MODEL", "gemini-1.5-flash")

    # Vector Search
    CHROMA_MODE: str = os.getenv("CHROMA_MODE", "persistent")
    CHROMA_PERSIST_DIR: Path = Path(os.getenv("CHROMA_PERSIST_DIR", "chroma_data"))
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    HYBRID_SEMANTIC_WEIGHT: float = 0.72

    UPLOAD_DIR: Path = Path("uploads")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)