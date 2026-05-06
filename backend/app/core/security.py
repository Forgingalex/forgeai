from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Request, Depends, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.core.exceptions import ForgeAIException
from app.core.logging_config import get_logger

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Bcrypt hashed password
    
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash
    
    Returns:
        Bcrypt hashed password
    
    Note:
        Uses bcrypt with automatic salt generation.
        Never store plain text passwords.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in token (typically {"sub": username})
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    
    Note:
        Token contains 'sub' (subject) field with username.
        Default expiration is 7 days (configurable).
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token string to decode
    
    Returns:
        Decoded payload dict if valid, None if invalid/expired
    
    Note:
        Returns None if token is invalid, expired, or malformed.
        Always check return value before using.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token in cookies.
    """
    token = request.cookies.get("access_token")
    if not token:
        logger.warning("No access_token cookie found")
        raise ForgeAIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            error_code="UNAUTHORIZED"
        )
    
    payload = decode_access_token(token)
    if payload is None:
        logger.warning("Invalid or expired token provided")
        raise ForgeAIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
            error_code="INVALID_TOKEN"
        )
    
    username: str = payload.get("sub")
    if username is None:
        logger.warning("Token missing 'sub' field")
        raise ForgeAIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid",
            error_code="INVALID_TOKEN"
        )
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        logger.warning(f"User not found: {username}")
        raise ForgeAIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            error_code="USER_NOT_FOUND"
        )
    
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {username}")
        raise ForgeAIException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            error_code="INACTIVE_USER"
        )
    
    logger.debug(f"Authenticated user: {username}")
    return user


