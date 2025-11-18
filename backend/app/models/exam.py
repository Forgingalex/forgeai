"""Exam models."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class ExamSession(Base):
    """Exam session model."""
    __tablename__ = "exam_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String(200), nullable=True)
    total_questions = Column(Integer, default=10)
    score = Column(Float, nullable=True)
    status = Column(String(20), default="in_progress")  # in_progress, completed, abandoned
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="exam_sessions")
    questions = relationship("ExamQuestion", back_populates="session", cascade="all, delete-orphan")


class ExamQuestion(Base):
    """Exam question model."""
    __tablename__ = "exam_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("exam_sessions.id"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    correct_answer = Column(Text, nullable=False)
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=True)
    feedback = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("ExamSession", back_populates="questions")

