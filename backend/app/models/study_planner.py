"""Study planner models."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class StudyPlan(Base):
    """Study plan model."""
    __tablename__ = "study_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(Text, nullable=True)
    topics = Column(JSON, nullable=True)  # List of topics to study
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    hours_per_day = Column(Integer, default=2)  # Hours available per day
    status = Column(String(20), default="active")  # active, completed, paused
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="study_plans")
    sessions = relationship("StudySession", back_populates="plan", cascade="all, delete-orphan")


class StudySession(Base):
    """Study session model."""
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("study_plans.id"), nullable=False)
    topic = Column(String(200), nullable=False)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=60)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    plan = relationship("StudyPlan", back_populates="sessions")

