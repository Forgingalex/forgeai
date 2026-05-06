"""Main FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.config import settings
from app.core.exceptions import ForgeAIException
from app.core.logging_config import get_logger, setup_logging

log_file = Path("logs/app.log")
setup_logging(log_level=settings.LOG_LEVEL if settings.DEBUG else "INFO", log_file=log_file)
logger = get_logger(__name__)

app = FastAPI(
    title="ForgeAI API",
    description="Production-grade AI study platform backend",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# handles cases where the cloud provider sends origins as a raw string or a list.
raw_origins = settings.CORS_ORIGINS
if isinstance(raw_origins, str):
    # Handle comma-separated strings "url1,url2" or a single "*"
    origins = [o.strip() for o in raw_origins.split(",")] if "," in raw_origins else [raw_origins]
else:
    # Fallback if it's already a list
    origins = raw_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.exception_handler(ForgeAIException)
async def forgeai_exception_handler(request: Request, exc: ForgeAIException):
    """Handle custom ForgeAI exceptions."""
    logger.error(
        "forgeai_exception",
        extra={"error": exc.detail, "error_code": exc.error_code, "path": request.url.path},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "error_code": exc.error_code,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors."""
    logger.warning("request_validation_error", extra={"errors": exc.errors(), "path": request.url.path})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.exception(
        "unexpected_error",
        extra={"error": str(exc), "path": request.url.path, "method": request.method},
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "error_code": "INTERNAL_ERROR",
        },
    )


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
        "version": "1.0.0",
    }
