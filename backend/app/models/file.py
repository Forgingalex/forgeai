"""File model."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class File(Base):
    """File model."""
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, pptx, txt, image, etc.
    file_size = Column(BigInteger, nullable=False)  # bytes
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    is_indexed = Column(Boolean, default=False)
    summary = Column(Text, nullable=True)
    extracted_text = Column(Text, nullable=True)
    
    # Metadata
    metadata = Column(Text, nullable=True)  # JSON string
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="files")
    workspace = relationship("Workspace", back_populates="files")

