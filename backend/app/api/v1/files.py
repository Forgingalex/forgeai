"""File upload and management endpoints."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.core.database import get_db
from app.core.exceptions import NotFoundError, ProcessingError, ValidationError
from app.core.logging_config import get_logger
from app.core.rate_limit import rate_limit
from app.models.user import User
from app.repositories.file_repository import FileRepository
from app.services.file_service import index_file, process_pdf, save_uploaded_file
from app.tasks.document_tasks import forge_document

logger = get_logger(__name__)
router = APIRouter()


class FileResponse(BaseModel):
    """Serialized uploaded file."""

    id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    is_processed: bool
    is_indexed: bool
    summary: Optional[str] = None

    class Config:
        from_attributes = True


class ForgeTaskResponse(BaseModel):
    """Background forging task status."""

    status: str
    task_id: Optional[str] = None
    file_id: int


def _as_bool(value: str) -> bool:
    return value.lower() in {"true", "1", "yes", "on"}


@router.post("/upload", response_model=FileResponse)
@rate_limit(max_requests=10, window_seconds=60)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    workspace_id: Optional[int] = Form(None),
    process_now: str = Form("false"),
    index_now: str = Form("false"),
    simple_summary: str = Form("false"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a file and optionally enqueue document forging."""
    logger.info(
        "file_upload_started",
        extra={"filename": file.filename, "user_id": current_user.id, "workspace_id": workspace_id},
    )
    try:
        file_content = await file.read()
    except Exception as exc:
        logger.error("file_read_failed", extra={"error": str(exc)})
        raise ValidationError("Failed to read file. Please try again.") from exc

    if len(file_content) > 50 * 1024 * 1024:
        raise ValidationError("File too large. Maximum size is 50MB.")

    file_metadata = await save_uploaded_file(file_content, file.filename or "upload", current_user.id)
    db_file = FileRepository(db).create(
        metadata=file_metadata,
        owner_id=current_user.id,
        workspace_id=workspace_id,
    )

    should_process = _as_bool(process_now)
    should_index = _as_bool(index_now)
    if db_file.file_type == "pdf" and (should_process or should_index):
        task = forge_document.delay(
            db_file.id,
            current_user.id,
            should_process,
            should_index,
            _as_bool(simple_summary),
        )
        logger.info(
            "document_forging_queued",
            extra={"file_id": db_file.id, "task_id": task.id, "user_id": current_user.id},
        )

    return db_file


@router.get("/", response_model=List[FileResponse])
async def get_files(
    workspace_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's files."""
    return FileRepository(db).list_owned(owner_id=current_user.id, workspace_id=workspace_id)


@router.post("/{file_id}/forge", response_model=ForgeTaskResponse)
async def forge_file_endpoint(
    file_id: int,
    process: bool = True,
    index: bool = True,
    simple: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Queue document processing and indexing in Celery."""
    db_file = FileRepository(db).get_owned(file_id=file_id, owner_id=current_user.id)
    if not db_file:
        raise NotFoundError("File", file_id)
    if db_file.file_type != "pdf":
        raise ValidationError("Only PDF files can be forged.")

    task = forge_document.delay(file_id, current_user.id, process, index, simple)
    return ForgeTaskResponse(status="queued", task_id=task.id, file_id=file_id)


@router.post("/{file_id}/process")
async def process_file(
    file_id: int,
    simple: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process a file immediately in the API process."""
    file_repo = FileRepository(db)
    db_file = file_repo.get_owned(file_id=file_id, owner_id=current_user.id)
    if not db_file:
        raise NotFoundError("File", file_id)
    if db_file.file_type != "pdf":
        raise ValidationError("File type not supported for processing.")

    try:
        with open(db_file.file_path, "rb") as handle:
            processed = await process_pdf(handle.read(), simple=simple)
        file_repo.mark_processed(
            db_file,
            summary=str(processed.get("summary", "")),
            extracted_text=str(processed.get("extracted_text", "")),
        )
        return {"status": "processed", "summary": processed.get("summary")}
    except Exception as exc:
        logger.error("file_processing_failed", extra={"file_id": file_id, "error": str(exc)}, exc_info=True)
        raise ProcessingError(f"Failed to process file: {exc}", file_type=db_file.file_type) from exc


@router.post("/{file_id}/index")
async def index_file_endpoint(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Index a file immediately in the API process."""
    file_repo = FileRepository(db)
    db_file = file_repo.get_owned(file_id=file_id, owner_id=current_user.id)
    if not db_file:
        raise NotFoundError("File", file_id)
    if db_file.file_type != "pdf":
        raise ValidationError("Only PDF files can be indexed.")

    with open(db_file.file_path, "rb") as handle:
        chunk_count = await index_file(
            handle.read(),
            db_file.original_filename,
            current_user.id,
            workspace_id=db_file.workspace_id,
            file_id=db_file.id,
        )

    file_repo.mark_indexed(db_file)
    return {"status": "indexed", "chunks": chunk_count}

