"""Celery tasks for document forging."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Union

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.core.logging_config import get_logger
from app.core.notifications import publish_user_event_sync
from app.repositories.file_repository import FileRepository
from app.services.document_service import DocumentProcessingService
from app.services.rag_service import RAGService

logger = get_logger(__name__)


@celery_app.task(name="app.tasks.document_tasks.forge_document")
def forge_document(
    file_id: int,
    user_id: int,
    process: bool = True,
    index: bool = True,
    simple_summary: bool = False,
) -> Dict[str, Union[int, str, bool]]:
    """Process and index an uploaded document in the background.

    Args:
        file_id: Database file id.
        user_id: Owner id.
        process: Whether to summarize/extract text.
        index: Whether to index chunks in ChromaDB.
        simple_summary: Whether to append a beginner-friendly summary.

    Returns:
        Task result metadata.
    """
    db = SessionLocal()
    file_repo = FileRepository(db)
    try:
        db_file = file_repo.get_owned(file_id=file_id, owner_id=user_id)
        if not db_file:
            raise ValueError(f"File not found: {file_id}")

        publish_user_event_sync(
            user_id,
            "document_forging_started",
            {
                "file_id": file_id,
                "filename": db_file.original_filename,
                "process": process,
                "index": index,
            },
        )

        file_bytes = Path(db_file.file_path).read_bytes()
        chunks_indexed = 0

        if process:
            processed = DocumentProcessingService().process_pdf_sync(
                file_bytes,
                simple=simple_summary,
            )
            file_repo.mark_processed(
                db_file,
                summary=processed.summary,
                extracted_text=processed.extracted_text,
            )

        if index:
            chunks_indexed = RAGService().index_pdf_bytes(
                pdf_bytes=file_bytes,
                source_name=db_file.original_filename,
                user_id=user_id,
                workspace_id=db_file.workspace_id,
                file_id=db_file.id,
            )
            file_repo.mark_indexed(db_file)

        publish_user_event_sync(
            user_id,
            "document_forging_completed",
            {
                "file_id": file_id,
                "filename": db_file.original_filename,
                "chunks_indexed": chunks_indexed,
                "is_processed": bool(process),
                "is_indexed": bool(index),
            },
        )
        logger.info(
            "document_forged",
            extra={"file_id": file_id, "user_id": user_id, "chunks_indexed": chunks_indexed},
        )
        return {
            "file_id": file_id,
            "status": "completed",
            "chunks_indexed": chunks_indexed,
            "processed": process,
            "indexed": index,
        }
    except Exception as exc:
        logger.error(
            "document_forging_failed",
            extra={"file_id": file_id, "user_id": user_id, "error": str(exc)},
            exc_info=True,
        )
        db_file = file_repo.get_owned(file_id=file_id, owner_id=user_id)
        if db_file:
            file_repo.mark_processing_failed(db_file, f"Document forging failed: {exc}")
        publish_user_event_sync(
            user_id,
            "document_forging_failed",
            {"file_id": file_id, "error": str(exc)},
        )
        raise
    finally:
        db.close()
