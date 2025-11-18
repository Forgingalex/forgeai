"""Main FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.core.config import settings
from app.api.v1 import api_router

app = FastAPI(
    title="ForgeAI API",
    description="Production-grade AI study platform backend",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "ForgeAI API"}


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": "ForgeAI API",
        "version": "1.0.0"
    }

