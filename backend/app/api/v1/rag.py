"""RAG endpoints for memory/knowledge base queries."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.ai_service import ask_with_context

router = APIRouter()


class RAGQuery(BaseModel):
    question: str
    top_k: int = 3


class RAGResponse(BaseModel):
    answer: str
    sources: List[str] = []


@router.post("/query", response_model=RAGResponse)
async def query_rag(
    query: RAGQuery,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Query the knowledge base using RAG."""
    try:
        answer = ask_with_context(query.question, top_k=query.top_k)
        
        # Extract sources from answer
        sources = []
        if "Sources used:" in answer:
            parts = answer.split("Sources used:")
            answer = parts[0].strip()
            sources_str = parts[1].strip() if len(parts) > 1 else ""
            sources = [s.strip() for s in sources_str.split(",") if s.strip()]
        elif "(Sources: none)" in answer:
            answer = answer.replace("(Sources: none)", "").strip()
        
        return RAGResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")

