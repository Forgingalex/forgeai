"""File upload and management endpoints."""
import logging
from fastapi import APIRouter, Depends, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.logging_config import get_logger
from app.core.exceptions import NotFoundError, ProcessingError, ValidationError
from app.core.rate_limit import rate_limit
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.file import File as FileModel
from app.models.workspace import Workspace
from app.services.file_service import save_uploaded_file, process_pdf, index_file
from pydantic import BaseModel

logger = get_logger(__name__)

router = APIRouter()


class FileResponse(BaseModel):
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


@router.post("/upload", response_model=FileResponse)
@rate_limit(max_requests=10, window_seconds=60)  # 10 uploads per minute
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    workspace_id: Optional[int] = Form(None),
    process_now: str = Form("false"),
    index_now: str = Form("false"),
    simple_summary: str = Form("false"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a file.
    
    Args:
        file: File to upload
        workspace_id: Optional workspace ID
        process_now: Whether to process immediately (PDF only)
        index_now: Whether to index immediately (PDF only)
        simple_summary: Whether to generate simple summary
    
    Returns:
        FileResponse with file metadata
    
    Raises:
        ValidationError: If file is too large or invalid
        ProcessingError: If processing fails
    """
    logger.info(f"File upload started: {file.filename} by user {current_user.id}")
    
    # Convert string booleans to actual booleans
    process_now_bool = process_now.lower() in ("true", "1", "yes")
    index_now_bool = index_now.lower() in ("true", "1", "yes")
    simple_summary_bool = simple_summary.lower() in ("true", "1", "yes")
    
    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise ValidationError("Failed to read file. Please try again.")
    
    # Check file size
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    if len(file_content) > MAX_FILE_SIZE:
        logger.warning(f"File too large: {len(file_content)} bytes")
        raise ValidationError(f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.0f}MB")
    
    # Save file
    file_metadata = await save_uploaded_file(file_content, file.filename, current_user.id)
    
    # Create database record
    db_file = FileModel(
        filename=file_metadata["filename"],
        original_filename=file_metadata["original_filename"],
        file_path=file_metadata["file_path"],
        file_type=file_metadata["file_type"],
        file_size=file_metadata["file_size"],
        owner_id=current_user.id,
        workspace_id=workspace_id,
    )
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    # Process if requested (after saving to DB so we can return file ID quickly)
    if process_now_bool and file_metadata["file_type"] == "pdf":
        try:
            logger.info(f"Processing PDF: {file.filename}")
            processed = await process_pdf(file_content, simple=simple_summary_bool)
            db_file.summary = processed.get("summary")
            db_file.extracted_text = processed.get("extracted_text")
            db_file.is_processed = True
            db.commit()
            db.refresh(db_file)
            logger.info(f"PDF processed successfully: {file.filename}")
        except Exception as e:
            # Log error but don't fail the upload
            logger.error(f"Error processing PDF {file.filename}: {e}", exc_info=True)
            db_file.is_processed = False
            db_file.summary = f"Error processing PDF: {str(e)}"
            db.commit()
            db.refresh(db_file)
    
    # Index if requested (can be done separately)
    if index_now_bool and file_metadata["file_type"] == "pdf":
        try:
            chunk_count = await index_file(
                file_content,
                db_file.original_filename,
                current_user.id
            )
            db_file.is_indexed = True
            db.commit()
        except Exception as e:
            print(f"Error indexing PDF: {e}")
    
    return db_file


@router.get("/", response_model=List[FileResponse])
async def get_files(
    workspace_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's files.
    
    Args:
        workspace_id: Optional workspace filter
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        List of user's files
    """
    query = db.query(FileModel).filter(FileModel.owner_id == current_user.id)
    if workspace_id:
        query = query.filter(FileModel.workspace_id == workspace_id)
    files = query.order_by(FileModel.created_at.desc()).all()
    logger.debug(f"Retrieved {len(files)} files for user {current_user.id}")
    return files


@router.post("/{file_id}/process")
async def process_file(
    file_id: int,
    simple: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process a file (extract text, summarize).
    
    Args:
        file_id: File ID to process
        simple: Whether to generate simple summary
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Processing status and summary
    
    Raises:
        NotFoundError: If file not found
        ProcessingError: If processing fails
    """
    db_file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.owner_id == current_user.id
    ).first()
    
    if not db_file:
        raise NotFoundError("File", file_id)
    
    # Read file
    with open(db_file.file_path, 'rb') as f:
        file_content = f.read()
    
    # Process
    if db_file.file_type == "pdf":
        try:
            logger.info(f"Processing file {file_id} for user {current_user.id}")
            processed = await process_pdf(file_content, simple=simple)
            db_file.summary = processed.get("summary")
            db_file.extracted_text = processed.get("extracted_text")
            db_file.is_processed = True
            db.commit()
            logger.info(f"File {file_id} processed successfully")
            return {"status": "processed", "summary": processed.get("summary")}
        except Exception as e:
            logger.error(f"Error processing file {file_id}: {e}", exc_info=True)
            raise ProcessingError(f"Failed to process file: {str(e)}", file_type=db_file.file_type)
    
    raise ValidationError("File type not supported for processing")


@router.post("/{file_id}/index")
async def index_file_endpoint(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Index a file into knowledge base.
    
    Args:
        file_id: File ID to index
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        Indexing status and chunk count
    
    Raises:
        NotFoundError: If file not found
    """
    db_file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.owner_id == current_user.id
    ).first()
    
    if not db_file:
        raise NotFoundError("File", file_id)
    
    # Read file
    with open(db_file.file_path, 'rb') as f:
        file_content = f.read()
    
    # Index
    chunk_count = await index_file(
        file_content,
        db_file.original_filename,
        current_user.id
    )
    
    db_file.is_indexed = True
    db.commit()
    
    return {"status": "indexed", "chunks": chunk_count}

