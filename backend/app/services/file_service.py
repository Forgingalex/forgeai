"""
File processing service.

Handles file upload, storage, and processing operations.
"""
import aiofiles
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.ai_service import extract_text_from_pdf_bytes, summarize_pdf, index_pdf_bytes_to_kb

logger = get_logger(__name__)


async def save_uploaded_file(file_content: bytes, filename: str, user_id: int) -> Dict[str, Any]:
    """
    Save uploaded file to disk and return metadata.
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        user_id: User ID for directory organization
    
    Returns:
        Dictionary with file metadata:
        - filename: Unique stored filename
        - original_filename: Original filename
        - file_path: Full path to saved file
        - file_type: File extension (lowercase)
        - file_size: File size in bytes
    """
    logger.debug(f"Saving file {filename} for user {user_id}")
    
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
    
    logger.info(f"File saved: {file_path} ({len(file_content)} bytes)")
    
    return {
        "filename": unique_filename,
        "original_filename": filename,
        "file_path": str(file_path),
        "file_type": file_type,
        "file_size": len(file_content),
    }


async def process_pdf(file_content: bytes, simple: bool = False) -> Dict[str, Any]:
    """
    Process PDF file - extract text and generate summary.
    
    Args:
        file_content: PDF file content as bytes
        simple: Whether to generate simple summary
    
    Returns:
        Dictionary with processing results:
        - summary: Generated summary text
        - extracted_text: Extracted text from PDF
        - is_processed: Whether processing succeeded
    
    Note:
        Runs sync summarize_pdf in thread pool to avoid blocking event loop.
        This allows async endpoints to handle PDF processing without blocking.
    """
    logger.debug(f"Processing PDF (simple={simple}, size={len(file_content)} bytes)")
    
    loop = None
    try:
        import asyncio
        loop = asyncio.get_event_loop()
    except RuntimeError:
        pass
    
    # Run sync function in thread pool to avoid blocking
    executor = ThreadPoolExecutor(max_workers=1)
    try:
        if loop:
            summary = await loop.run_in_executor(
                executor, 
                summarize_pdf, 
                file_content, 
                simple
            )
        else:
            # Fallback if no event loop
            summary = summarize_pdf(file_content, simple=simple)
        
        extracted_text = extract_text_from_pdf_bytes(file_content)
        
        logger.info(f"PDF processed successfully (summary length: {len(summary)} chars)")
        
        return {
            "summary": summary,
            "extracted_text": extracted_text,
            "is_processed": True,
        }
    except Exception as e:
        logger.error(f"Error processing PDF: {e}", exc_info=True)
        return {
            "summary": f"Error processing PDF: {str(e)}",
            "extracted_text": "",
            "is_processed": False,
        }
    finally:
        executor.shutdown(wait=False)


async def index_file(file_content: bytes, source_name: str, user_id: int) -> int:
    """
    Index file into knowledge base for RAG queries.
    
    Args:
        file_content: File content as bytes
        source_name: Source identifier for the file
        user_id: User ID (for logging)
    
    Returns:
        Number of chunks indexed
    
    Note:
        Currently only supports PDF files.
        Indexes text chunks for semantic search.
    """
    logger.info(f"Indexing file {source_name} for user {user_id}")
    chunk_count = index_pdf_bytes_to_kb(file_content, source_name=source_name)
    logger.info(f"Indexed {chunk_count} chunks from {source_name}")
    return chunk_count

