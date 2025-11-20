"""Custom exceptions for the application."""
from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class ForgeAIException(HTTPException):
    """Base exception for ForgeAI application."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize ForgeAI exception.
        
        Args:
            status_code: HTTP status code
            detail: Error message
            error_code: Optional error code for client handling
            headers: Optional HTTP headers
        """
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class ValidationError(ForgeAIException):
    """Raised when input validation fails."""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="VALIDATION_ERROR",
        )
        self.field = field


class AuthenticationError(ForgeAIException):
    """Raised when authentication fails."""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTHENTICATION_ERROR",
        )


class AuthorizationError(ForgeAIException):
    """Raised when user lacks permission."""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_ERROR",
        )


class NotFoundError(ForgeAIException):
    """Raised when resource is not found."""
    
    def __init__(self, resource: str, identifier: Any = None):
        detail = f"{resource} not found"
        if identifier is not None:
            detail += f": {identifier}"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="NOT_FOUND",
        )


class ProcessingError(ForgeAIException):
    """Raised when file processing fails."""
    
    def __init__(self, detail: str, file_type: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="PROCESSING_ERROR",
        )
        self.file_type = file_type


class AIServiceError(ForgeAIException):
    """Raised when AI service fails."""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_code="AI_SERVICE_ERROR",
        )

