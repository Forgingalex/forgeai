"""RAG endpoints for local knowledge retrieval."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.rag_service import RAGService

router = APIRouter()


class RAGQuery(BaseModel):
    """RAG query request."""

    question: str
    top_k: int = 5
    workspace_id: Optional[int] = None


class RAGSource(BaseModel):
    """Retrieved source metadata."""

    source: str
    score: float
    semantic_score: float
    keyword_score: float


class RAGResponse(BaseModel):
    """RAG answer response."""

    answer: str
    sources: List[str] = []
    matches: List[RAGSource] = []


@router.post("/query", response_model=RAGResponse)
async def query_rag(
    query: RAGQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Query the scoped local knowledge base."""
    answer = await RAGService().answer_question(
        question=query.question,
        top_k=query.top_k,
        user_id=current_user.id,
        workspace_id=query.workspace_id,
    )
    return RAGResponse(
        answer=answer.answer,
        sources=answer.sources,
        matches=[
            RAGSource(
                source=result.source,
                score=result.score,
                semantic_score=result.semantic_score,
                keyword_score=result.keyword_score,
            )
            for result in answer.results
        ],
    )
