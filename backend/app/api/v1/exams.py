"""Exam endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.exam import ExamSession, ExamQuestion
from app.services.ai_service import ask_brain

router = APIRouter()


class ExamCreate(BaseModel):
    title: str
    topic: Optional[str] = None
    total_questions: int = 10


class ExamQuestionResponse(BaseModel):
    id: int
    question_number: int
    question: str
    user_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    feedback: Optional[str] = None
    
    class Config:
        from_attributes = True


class ExamSessionResponse(BaseModel):
    id: int
    title: str
    topic: Optional[str] = None
    total_questions: int
    score: Optional[float] = None
    status: str
    questions: List[ExamQuestionResponse] = []
    
    class Config:
        from_attributes = True


@router.post("/", response_model=ExamSessionResponse)
async def create_exam(
    exam_data: ExamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new exam session."""
    # Generate questions using AI
    prompt = f"Generate {exam_data.total_questions} exam questions about {exam_data.topic or 'general knowledge'}. Format: Q1: [question] | A1: [answer]"
    response = await ask_brain(prompt)
    
    # Parse questions (simplified - in production, use better parsing)
    questions = []
    lines = response.split('\n')
    current_q = None
    current_a = None
    
    for line in lines:
        if 'Q' in line and ':' in line:
            if current_q and current_a:
                questions.append((current_q, current_a))
            current_q = line.split(':', 1)[1].strip()
        elif 'A' in line and ':' in line:
            current_a = line.split(':', 1)[1].strip()
    
    if current_q and current_a:
        questions.append((current_q, current_a))
    
    # Create exam session
    exam_session = ExamSession(
        title=exam_data.title,
        topic=exam_data.topic,
        total_questions=len(questions),
        user_id=current_user.id,
    )
    db.add(exam_session)
    db.commit()
    db.refresh(exam_session)
    
    # Create questions
    for idx, (question, answer) in enumerate(questions[:exam_data.total_questions], 1):
        exam_question = ExamQuestion(
            session_id=exam_session.id,
            question_number=idx,
            question=question,
            correct_answer=answer,
        )
        db.add(exam_question)
    
    db.commit()
    db.refresh(exam_session)
    return exam_session


@router.get("/", response_model=List[ExamSessionResponse])
async def get_exams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's exam sessions."""
    exams = db.query(ExamSession).filter(
        ExamSession.user_id == current_user.id
    ).order_by(ExamSession.started_at.desc()).all()
    return exams


@router.get("/{exam_id}", response_model=ExamSessionResponse)
async def get_exam(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get an exam session by ID."""
    exam = db.query(ExamSession).filter(
        ExamSession.id == exam_id,
        ExamSession.user_id == current_user.id
    ).first()
    
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    return exam


class SubmitAnswerRequest(BaseModel):
    question_id: int
    answer: str


@router.post("/{exam_id}/submit-answer")
async def submit_answer(
    exam_id: int,
    request: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit an answer to an exam question."""
    exam = db.query(ExamSession).filter(
        ExamSession.id == exam_id,
        ExamSession.user_id == current_user.id
    ).first()
    
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    question = db.query(ExamQuestion).filter(
        ExamQuestion.id == request.question_id,
        ExamQuestion.session_id == exam_id
    ).first()
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    question.user_answer = request.answer
    
    # Grade answer using AI
    grading_prompt = f"Question: {question.question}\nCorrect Answer: {question.correct_answer}\nStudent Answer: {request.answer}\n\nGrade this answer (correct/incorrect) and provide brief feedback."
    grading_response = await ask_brain(grading_prompt)
    
    # Simple parsing (in production, use better parsing)
    is_correct = "correct" in grading_response.lower()
    question.is_correct = is_correct
    question.feedback = grading_response
    
    db.commit()
    
    return {"is_correct": is_correct, "feedback": grading_response}


@router.post("/{exam_id}/complete")
async def complete_exam(
    exam_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete an exam and calculate score."""
    exam = db.query(ExamSession).filter(
        ExamSession.id == exam_id,
        ExamSession.user_id == current_user.id
    ).first()
    
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    # Calculate score
    questions = db.query(ExamQuestion).filter(
        ExamQuestion.session_id == exam_id
    ).all()
    
    if not questions:
        raise HTTPException(status_code=400, detail="No questions found")
    
    correct_count = sum(1 for q in questions if q.is_correct)
    total_count = len(questions)
    score = (correct_count / total_count) * 100 if total_count > 0 else 0
    
    exam.score = score
    exam.status = "completed"
    exam.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(exam)
    
    return {"score": score, "correct": correct_count, "total": total_count}

