"""Unit tests for security utilities."""
import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)
from datetime import timedelta


def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    # Hash should be different from original
    assert hashed != password
    
    # Should verify correctly
    assert verify_password(password, hashed) is True
    
    # Wrong password should fail
    assert verify_password("wrongpassword", hashed) is False


def test_jwt_token_creation():
    """Test JWT token creation and decoding."""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    # Token should be a string
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Should decode correctly
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "testuser"
    assert "exp" in payload


def test_jwt_token_expiration():
    """Test JWT token with custom expiration."""
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=30)
    token = create_access_token(data, expires_delta=expires_delta)
    
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "testuser"


def test_invalid_token():
    """Test decoding invalid token."""
    invalid_token = "invalid.token.here"
    payload = decode_access_token(invalid_token)
    assert payload is None

