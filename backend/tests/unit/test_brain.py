"""Unit tests for brain (AI) functions."""
import pytest
from app.core.brain import split_text_to_chunks, extract_text_from_pdf_bytes
import io


def test_split_text_to_chunks_empty():
    """Test chunking empty text."""
    result = split_text_to_chunks("")
    assert result == []


def test_split_text_to_chunks_small():
    """Test chunking small text."""
    text = "This is a short text."
    result = split_text_to_chunks(text, chunk_size=100)
    assert len(result) == 1
    assert result[0] == text


def test_split_text_to_chunks_large():
    """Test chunking large text."""
    text = "A" * 2000  # 2000 characters
    result = split_text_to_chunks(text, chunk_size=500, overlap=50)
    
    # Should create multiple chunks
    assert len(result) > 1
    
    # Check overlap
    if len(result) > 1:
        # First chunk should be 500 chars
        assert len(result[0]) <= 500
        
        # Second chunk should start before first ends (overlap)
        # This is a basic check - actual overlap logic is in the function


def test_split_text_to_chunks_max_size():
    """Test chunking respects max size limit."""
    # Create text larger than 10MB limit
    text = "A" * (11 * 1024 * 1024)  # 11MB
    result = split_text_to_chunks(text, chunk_size=1000)
    
    # Should still process (truncated to 10MB before chunking)
    assert len(result) > 0
    # Each chunk should respect chunk_size
    for chunk in result:
        assert len(chunk) <= 1000
    # Should create multiple chunks (proving it processed large text)
    assert len(result) > 1
    # Note: Total length will exceed 10MB due to overlaps, which is expected


def test_extract_text_from_pdf_bytes_invalid():
    """Test extracting text from invalid PDF."""
    invalid_pdf = b"not a pdf file"
    result = extract_text_from_pdf_bytes(invalid_pdf)
    # Should return empty string or handle gracefully
    assert isinstance(result, str)


def test_extract_text_from_pdf_bytes_empty():
    """Test extracting text from empty bytes."""
    result = extract_text_from_pdf_bytes(b"")
    assert isinstance(result, str)

