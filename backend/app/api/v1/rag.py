"""RAG endpoints for memory/knowledge base queries."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.core.logging_config import get_logger
from app.core.exceptions import AIServiceError
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.services.ai_service import ask_with_context

logger = get_logger(__name__)

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
    """
    Query the knowledge base using RAG (Retrieval-Augmented Generation).
    
    Args:
        query: RAG query with question and top_k
        current_user: Current authenticated user
        db: Database session
    
    Returns:
        RAG response with answer and sources
    
    Raises:
        AIServiceError: If AI service fails
    """
    logger.info(f"RAG query from user {current_user.id}: {query.question[:50]}...")
    
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
        
        logger.debug(f"RAG query completed, found {len(sources)} sources")
        return RAGResponse(answer=answer, sources=sources)
    except Exception as e:
        logger.error(f"RAG query failed: {e}", exc_info=True)
        raise AIServiceError(f"RAG query failed: {str(e)}")

