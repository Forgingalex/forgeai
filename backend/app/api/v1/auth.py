"""Authentication endpoints."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from app.core.database import get_db
from app.core.logging_config import get_logger
from app.core.exceptions import AuthenticationError, ValidationError
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.core.config import settings
from app.models.user import User

logger = get_logger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str = None
    is_active: bool
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        token: JWT access token from Authorization header
        db: Database session
    
    Returns:
        User object for authenticated user
    
    Raises:
        AuthenticationError: If token is invalid or user not found
    """
    payload = decode_access_token(token)
    if payload is None:
        logger.warning("Invalid token provided")
        raise AuthenticationError("Could not validate credentials")
    
    username: str = payload.get("sub")
    if username is None:
        logger.warning("Token missing 'sub' field")
        raise AuthenticationError("Could not validate credentials")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        logger.warning(f"User not found: {username}")
        raise AuthenticationError("Could not validate credentials")
    
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {username}")
        raise AuthenticationError("User account is inactive")
    
    logger.debug(f"Authenticated user: {username}")
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login and get access token.
    
    Args:
        form_data: Login credentials (username, password)
        db: Database session
    
    Returns:
        JWT access token
    
    Raises:
        AuthenticationError: If credentials are invalid
    """
    logger.info(f"Login attempt: {form_data.username}")
    
    user = db.query(User).filter(User.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed: invalid credentials for {form_data.username}")
        raise AuthenticationError("Incorrect username or password")
    
    if not user.is_active:
        logger.warning(f"Login failed: inactive user {form_data.username}")
        raise AuthenticationError("User account is inactive")
    
    access_token = create_access_token(data={"sub": user.username})
    logger.info(f"Login successful: {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

