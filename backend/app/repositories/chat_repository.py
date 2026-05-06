"""Chat persistence repository."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable, List, Optional

from sqlalchemy.orm import Session

from app.models.chat import ChatMessage, ChatSession


class ChatRepository:
    """Repository for chat sessions and messages."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_session(self, user_id: int, workspace_id: Optional[int] = None) -> ChatSession:
        """Create and persist a chat session."""
        session = ChatSession(user_id=user_id, workspace_id=workspace_id)
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def list_sessions(self, user_id: int, workspace_id: Optional[int] = None) -> List[ChatSession]:
        """Return chat sessions owned by a user."""
        query = self.db.query(ChatSession).filter(ChatSession.user_id == user_id)
        if workspace_id is not None:
            query = query.filter(ChatSession.workspace_id == workspace_id)
        return query.order_by(ChatSession.updated_at.desc().nullslast(), ChatSession.created_at.desc()).all()

    def get_session(self, session_id: int) -> Optional[ChatSession]:
        """Return a chat session by id."""
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()

    def get_owned_session(self, session_id: int, user_id: int) -> Optional[ChatSession]:
        """Return a session only when it belongs to the user."""
        return (
            self.db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
            .first()
        )

    def list_messages(self, session_id: int, limit: Optional[int] = None) -> List[ChatMessage]:
        """Return messages for a session in chronological order."""
        query = (
            self.db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        if limit is None:
            return query.all()
        return query.limit(limit).all()

    def add_message(
        self,
        session_id: int,
        role: str,
        content: str,
        sources: Optional[Iterable[str]] = None,
        metadata: Optional[dict] = None,
    ) -> ChatMessage:
        """Persist a chat message and update session activity."""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            sources=list(sources) if sources else None,
            message_metadata=metadata,
        )
        session = self.get_session(session_id)
        if session:
            session.updated_at = datetime.now(timezone.utc)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

