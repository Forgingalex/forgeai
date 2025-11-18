"""File processing service."""
import aiofiles
import hashlib
from pathlib import Path
from typing import Optional
from app.core.config import settings
from app.services.ai_service import extract_text_from_pdf_bytes, summarize_pdf, index_pdf_bytes_to_kb


async def save_uploaded_file(file_content: bytes, filename: str, user_id: int) -> dict:
    """Save uploaded file and return metadata."""
    # Create user-specific directory
    user_dir = settings.UPLOAD_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    file_hash = hashlib.md5(file_content).hexdigest()[:8]
    file_ext = Path(filename).suffix
    unique_filename = f"{file_hash}_{filename}"
    file_path = user_dir / unique_filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)
    
    # Determine file type
    file_type = file_ext.lstrip('.').lower()
    
    return {
        "filename": unique_filename,
        "original_filename": filename,
        "file_path": str(file_path),
        "file_type": file_type,
        "file_size": len(file_content),
    }


async def process_pdf(file_content: bytes, simple: bool = False) -> dict:
    """Process PDF file - uses existing summarize_pdf function."""
    summary = summarize_pdf(file_content, simple=simple)
    extracted_text = extract_text_from_pdf_bytes(file_content)
    
    return {
        "summary": summary,
        "extracted_text": extracted_text,
        "is_processed": True,
    }


async def index_file(file_content: bytes, source_name: str, user_id: int) -> int:
    """Index file into knowledge base - uses existing function."""
    chunk_count = index_pdf_bytes_to_kb(file_content, source_name=source_name)
    return chunk_count

