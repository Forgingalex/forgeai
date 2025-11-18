"""Workspace model."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Workspace(Base):
    """Workspace model."""
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="workspaces")
    files = relationship("File", back_populates="workspace", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="workspace", cascade="all, delete-orphan")

