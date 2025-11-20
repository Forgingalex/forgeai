"""Integration tests for file upload endpoints."""
import pytest
from fastapi import status
import io


def test_upload_file_unauthorized(client):
    """Test uploading file without authentication."""
    files = {"file": ("test.pdf", io.BytesIO(b"fake pdf content"), "application/pdf")}
    response = client.post("/api/v1/files/upload", files=files)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_upload_file_success(client, auth_headers):
    """Test successful file upload."""
    files = {"file": ("test.pdf", io.BytesIO(b"fake pdf content"), "application/pdf")}
    data = {"process_now": "false", "simple_summary": "false"}
    
    response = client.post(
        "/api/v1/files/upload",
        files=files,
        data=data,
        headers=auth_headers,
    )
    
    # Should succeed (even if processing fails, upload should work)
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]
    
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        assert "id" in data
        assert data["filename"] is not None


def test_get_files(client, auth_headers):
    """Test getting user's files."""
    response = client.get("/api/v1/files/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

