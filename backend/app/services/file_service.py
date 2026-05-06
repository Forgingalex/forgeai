"""File storage and document processing service functions."""

from __future__ import annotations

import aiofiles
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.document_service import DocumentProcessingService
from app.services.rag_service import RAGService

logger = get_logger(__name__)


async def save_uploaded_file(file_content: bytes, filename: str, user_id: int) -> Dict[str, Any]:
    """Save uploaded file to disk and return metadata.

    Args:
        file_content: File content as bytes.
        filename: Original filename.
        user_id: User ID for directory organization.

    Returns:
        Dictionary with stored filename, original filename, path, type, and size.
    """
    logger.debug("saving_uploaded_file", extra={"filename": filename, "user_id": user_id})

    user_dir = settings.UPLOAD_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    file_hash = hashlib.sha256(file_content).hexdigest()[:12]
    file_ext = Path(filename).suffix
    unique_filename = f"{file_hash}_{filename}"
    file_path = user_dir / unique_filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(file_content)

    file_type = file_ext.lstrip(".").lower()
    logger.info(
        "uploaded_file_saved",
        extra={"file_path": str(file_path), "file_size": len(file_content), "user_id": user_id},
    )

    return {
        "filename": unique_filename,
        "original_filename": filename,
        "file_path": str(file_path),
        "file_type": file_type,
        "file_size": len(file_content),
    }


async def process_pdf(file_content: bytes, simple: bool = False) -> Dict[str, Any]:
    """Process a PDF file by extracting text and generating a summary.

    Args:
        file_content: PDF file content as bytes.
        simple: Whether to append a beginner-friendly summary.

    Returns:
        Processing result dictionary.
    """
    logger.debug(
        "processing_pdf_inline",
        extra={"simple": simple, "file_size": len(file_content)},
    )
    try:
        result = await DocumentProcessingService().process_pdf(file_content, simple=simple)
        logger.info(
            "pdf_processed_inline",
            extra={"summary_length": len(result.summary), "text_length": len(result.extracted_text)},
        )
        return {
            "summary": result.summary,
            "extracted_text": result.extracted_text,
            "is_processed": result.is_processed,
        }
    except Exception as exc:
        logger.error("pdf_processing_failed", extra={"error": str(exc)}, exc_info=True)
        return {
            "summary": f"Error processing PDF: {str(exc)}",
            "extracted_text": "",
            "is_processed": False,
        }


async def index_file(
    file_content: bytes,
    source_name: str,
    user_id: int,
    workspace_id: Optional[int] = None,
    file_id: Optional[int] = None,
) -> int:
    """Index a PDF file into the knowledge base for RAG queries.

    Args:
        file_content: File content as bytes.
        source_name: Source identifier for the file.
        user_id: User ID.
        workspace_id: Optional workspace scope.
        file_id: Optional database file id.

    Returns:
        Number of chunks indexed.
    """
    logger.info(
        "indexing_file",
        extra={"source_name": source_name, "user_id": user_id, "workspace_id": workspace_id},
    )
    chunk_count = RAGService().index_pdf_bytes(
        pdf_bytes=file_content,
        source_name=source_name,
        user_id=user_id,
        workspace_id=workspace_id,
        file_id=file_id,
    )
    logger.info("file_indexed", extra={"source_name": source_name, "chunk_count": chunk_count})
    return chunk_count
