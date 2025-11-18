"""Flashcard endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.flashcard import FlashcardSet, Flashcard

router = APIRouter()


class FlashcardSetCreate(BaseModel):
    name: str
    description: Optional[str] = None


class FlashcardCreate(BaseModel):
    front: str
    back: str


class FlashcardResponse(BaseModel):
    id: int
    front: str
    back: str
    review_count: int
    
    class Config:
        from_attributes = True


class FlashcardSetResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    flashcards: List[FlashcardResponse] = []
    
    class Config:
        from_attributes = True


@router.post("/sets", response_model=FlashcardSetResponse)
async def create_set(
    set_data: FlashcardSetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a flashcard set."""
    flashcard_set = FlashcardSet(
        name=set_data.name,
        description=set_data.description,
        owner_id=current_user.id,
    )
    db.add(flashcard_set)
    db.commit()
    db.refresh(flashcard_set)
    return flashcard_set


@router.get("/sets", response_model=List[FlashcardSetResponse])
async def get_sets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's flashcard sets."""
    sets = db.query(FlashcardSet).filter(
        FlashcardSet.owner_id == current_user.id
    ).all()
    return sets


@router.get("/sets/{set_id}", response_model=FlashcardSetResponse)
async def get_set(
    set_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a flashcard set by ID."""
    flashcard_set = db.query(FlashcardSet).filter(
        FlashcardSet.id == set_id,
        FlashcardSet.owner_id == current_user.id
    ).first()
    
    if not flashcard_set:
        raise HTTPException(status_code=404, detail="Flashcard set not found")
    
    return flashcard_set


@router.post("/sets/{set_id}/cards", response_model=FlashcardResponse)
async def add_card(
    set_id: int,
    card_data: FlashcardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a flashcard to a set."""
    flashcard_set = db.query(FlashcardSet).filter(
        FlashcardSet.id == set_id,
        FlashcardSet.owner_id == current_user.id
    ).first()
    
    if not flashcard_set:
        raise HTTPException(status_code=404, detail="Flashcard set not found")
    
    card = Flashcard(
        set_id=set_id,
        front=card_data.front,
        back=card_data.back,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@router.delete("/sets/{set_id}")
async def delete_set(
    set_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a flashcard set."""
    flashcard_set = db.query(FlashcardSet).filter(
        FlashcardSet.id == set_id,
        FlashcardSet.owner_id == current_user.id
    ).first()
    
    if not flashcard_set:
        raise HTTPException(status_code=404, detail="Flashcard set not found")
    
    db.delete(flashcard_set)
    db.commit()
    return {"message": "Flashcard set deleted"}


@router.delete("/cards/{card_id}")
async def delete_card(
    card_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a flashcard."""
    card = db.query(Flashcard).join(FlashcardSet).filter(
        Flashcard.id == card_id,
        FlashcardSet.owner_id == current_user.id
    ).first()
    
    if not card:
        raise HTTPException(status_code=404, detail="Flashcard not found")
    
    db.delete(card)
    db.commit()
    return {"message": "Flashcard deleted"}

