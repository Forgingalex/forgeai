"""Flashcard models."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class FlashcardSet(Base):
    """Flashcard set model."""
    __tablename__ = "flashcard_sets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="flashcard_sets")
    flashcards = relationship("Flashcard", back_populates="set", cascade="all, delete-orphan")


class Flashcard(Base):
    """Flashcard model."""
    __tablename__ = "flashcards"
    
    id = Column(Integer, primary_key=True, index=True)
    set_id = Column(Integer, ForeignKey("flashcard_sets.id"), nullable=False)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    
    # Spaced repetition
    last_reviewed = Column(DateTime(timezone=True), nullable=True)
    next_review = Column(DateTime(timezone=True), nullable=True)
    review_count = Column(Integer, default=0)
    ease_factor = Column(Integer, default=250)  # SM-2 algorithm
    interval_days = Column(Integer, default=1)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    set = relationship("FlashcardSet", back_populates="flashcards")

