"""Study planner endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.study_planner import StudyPlan, StudySession
from app.services.ai_service import ask_brain

router = APIRouter()


class StudyPlanCreate(BaseModel):
    title: str
    description: Optional[str] = None
    topics: List[str] = []
    start_date: datetime
    end_date: datetime
    hours_per_day: int = 2


class StudySessionResponse(BaseModel):
    id: int
    topic: str
    scheduled_date: datetime
    duration_minutes: int
    completed: bool
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class StudyPlanResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    topics: List[str] = []
    start_date: datetime
    end_date: datetime
    hours_per_day: int
    status: str
    sessions: List[StudySessionResponse] = []
    
    class Config:
        from_attributes = True


@router.post("/", response_model=StudyPlanResponse)
async def create_plan(
    plan_data: StudyPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new study plan."""
    # Generate study schedule using AI
    topics_str = ", ".join(plan_data.topics) if plan_data.topics else "general topics"
    days_diff = (plan_data.end_date - plan_data.start_date).days
    
    prompt = f"""Create a study schedule for the following:
Topics: {topics_str}
Start Date: {plan_data.start_date.strftime('%Y-%m-%d')}
End Date: {plan_data.end_date.strftime('%Y-%m-%d')}
Days Available: {days_diff}
Hours per day: {plan_data.hours_per_day}

Generate a daily schedule. Format: Day 1: [topic] - [duration] minutes | Day 2: [topic] - [duration] minutes"""
    
    response = await ask_brain(prompt)
    
    # Create study plan
    study_plan = StudyPlan(
        title=plan_data.title,
        description=plan_data.description,
        topics=plan_data.topics,
        start_date=plan_data.start_date,
        end_date=plan_data.end_date,
        hours_per_day=plan_data.hours_per_day,
        user_id=current_user.id,
    )
    db.add(study_plan)
    db.commit()
    db.refresh(study_plan)
    
    # Parse and create sessions
    current_date = plan_data.start_date
    lines = response.split('\n')
    session_num = 0
    
    for line in lines:
        if 'Day' in line and ':' in line:
            parts = line.split(':')
            if len(parts) >= 2:
                topic_info = parts[1].strip()
                # Extract topic and duration
                if ' - ' in topic_info:
                    topic, duration_str = topic_info.split(' - ', 1)
                    topic = topic.strip()
                    duration_str = duration_str.replace('minutes', '').replace('min', '').strip()
                    try:
                        duration = int(duration_str)
                    except:
                        duration = 60
                else:
                    topic = topic_info
                    duration = 60
                
                session = StudySession(
                    plan_id=study_plan.id,
                    topic=topic,
                    scheduled_date=current_date,
                    duration_minutes=duration,
                )
                db.add(session)
                session_num += 1
                current_date += timedelta(days=1)
                
                if current_date > plan_data.end_date:
                    break
    
    # If no sessions were created, create default ones
    if session_num == 0:
        topics_list = plan_data.topics if plan_data.topics else ["General Study"]
        topics_per_day = max(1, len(topics_list) // max(1, days_diff))
        current_date = plan_data.start_date
        
        for i in range(min(days_diff, len(topics_list))):
            topic_idx = i % len(topics_list)
            session = StudySession(
                plan_id=study_plan.id,
                topic=topics_list[topic_idx],
                scheduled_date=current_date,
                duration_minutes=plan_data.hours_per_day * 60,
            )
            db.add(session)
            current_date += timedelta(days=1)
    
    db.commit()
    db.refresh(study_plan)
    return study_plan


@router.get("/", response_model=List[StudyPlanResponse])
async def get_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's study plans."""
    plans = db.query(StudyPlan).filter(
        StudyPlan.user_id == current_user.id
    ).order_by(StudyPlan.created_at.desc()).all()
    return plans


@router.get("/{plan_id}", response_model=StudyPlanResponse)
async def get_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a study plan by ID."""
    plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    
    return plan


@router.post("/{plan_id}/sessions/{session_id}/complete")
async def complete_session(
    plan_id: int,
    session_id: int,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a study session as completed."""
    plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    
    session = db.query(StudySession).filter(
        StudySession.id == session_id,
        StudySession.plan_id == plan_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Study session not found")
    
    session.completed = True
    session.completed_at = datetime.utcnow()
    if notes:
        session.notes = notes
    
    db.commit()
    return {"message": "Session completed"}


@router.delete("/{plan_id}")
async def delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a study plan."""
    plan = db.query(StudyPlan).filter(
        StudyPlan.id == plan_id,
        StudyPlan.user_id == current_user.id
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Study plan not found")
    
    db.delete(plan)
    db.commit()
    return {"message": "Study plan deleted"}

