"""File upload and management endpoints."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.file import File as FileModel
from app.models.workspace import Workspace
from app.services.file_service import save_uploaded_file, process_pdf, index_file
from pydantic import BaseModel

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
async def upload_file(
    file: UploadFile = File(...),
    workspace_id: Optional[int] = Form(None),
    process_now: bool = Form(False),
    index_now: bool = Form(False),
    simple_summary: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a file."""
    # Read file content
    file_content = await file.read()
    
    # Check file size
    if len(file_content) > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(status_code=400, detail="File too large")
    
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
    
    # Process if requested
    if process_now and file_metadata["file_type"] == "pdf":
        processed = await process_pdf(file_content, simple=simple_summary)
        db_file.summary = processed.get("summary")
        db_file.extracted_text = processed.get("extracted_text")
        db_file.is_processed = True
    
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    # Index if requested
    if index_now and file_metadata["file_type"] == "pdf":
        chunk_count = await index_file(
            file_content,
            db_file.original_filename,
            current_user.id
        )
        db_file.is_indexed = True
        db.commit()
    
    return db_file


@router.get("/", response_model=List[FileResponse])
async def get_files(
    workspace_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's files."""
    query = db.query(FileModel).filter(FileModel.owner_id == current_user.id)
    if workspace_id:
        query = query.filter(FileModel.workspace_id == workspace_id)
    files = query.order_by(FileModel.created_at.desc()).all()
    return files


@router.post("/{file_id}/process")
async def process_file(
    file_id: int,
    simple: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process a file (extract text, summarize)."""
    db_file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.owner_id == current_user.id
    ).first()
    
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Read file
    with open(db_file.file_path, 'rb') as f:
        file_content = f.read()
    
    # Process
    if db_file.file_type == "pdf":
        processed = await process_pdf(file_content, simple=simple)
        db_file.summary = processed.get("summary")
        db_file.extracted_text = processed.get("extracted_text")
        db_file.is_processed = True
        db.commit()
        return {"status": "processed", "summary": processed.get("summary")}
    
    raise HTTPException(status_code=400, detail="File type not supported for processing")


@router.post("/{file_id}/index")
async def index_file_endpoint(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Index a file into knowledge base."""
    db_file = db.query(FileModel).filter(
        FileModel.id == file_id,
        FileModel.owner_id == current_user.id
    ).first()
    
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
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

