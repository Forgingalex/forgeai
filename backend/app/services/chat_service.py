"""Chat orchestration service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import AsyncGenerator, Dict, List, Optional

from app.core.exceptions import NotFoundError
from app.repositories.chat_repository import ChatRepository
from app.services.ai_service import AIProvider, AIService, ReasoningMode
from app.services.rag_service import RAGService


@dataclass(frozen=True)
class ChatTurnResult:
    """Completed chat turn metadata."""

    content: str
    sources: List[str]
    metadata: Dict[str, str]


class ChatService:
    """Coordinates chat persistence, RAG, and AI streaming."""

    def __init__(
        self,
        chat_repository: ChatRepository,
        ai_service: Optional[AIService] = None,
        rag_service: Optional[RAGService] = None,
    ) -> None:
        self.chat_repository = chat_repository
        self.ai_service = ai_service or AIService()
        self.rag_service = rag_service or RAGService(ai_service=self.ai_service)

    def create_session(self, user_id: int, workspace_id: Optional[int] = None):
        """Create a chat session."""
        return self.chat_repository.create_session(user_id=user_id, workspace_id=workspace_id)

    def list_sessions(self, user_id: int, workspace_id: Optional[int] = None):
        """List chat sessions."""
        return self.chat_repository.list_sessions(user_id=user_id, workspace_id=workspace_id)

    def list_messages(self, session_id: int, user_id: int):
        """List messages for an owned session."""
        session = self.chat_repository.get_owned_session(session_id=session_id, user_id=user_id)
        if not session:
            raise NotFoundError("Chat session", session_id)
        return self.chat_repository.list_messages(session_id=session_id)

    async def stream_turn(
        self,
        session_id: int,
        user_id: int,
        message: str,
        mode: ReasoningMode = ReasoningMode.CHAT,
        top_k: int = 5,
    ) -> AsyncGenerator[Dict[str, object], None]:
        """Persist and stream a chat turn.

        Args:
            session_id: Chat session id.
            user_id: User id for ownership and RAG scope.
            message: User message.
            mode: Chat mode from the frontend.
            top_k: RAG retrieval count.

        Yields:
            WebSocket-friendly event payloads.
        """
        session = self.chat_repository.get_owned_session(session_id=session_id, user_id=user_id)
        if not session:
            raise NotFoundError("Chat session", session_id)

        self.chat_repository.add_message(session_id=session_id, role="user", content=message)

        if mode is ReasoningMode.SEARCH:
            answer = await self.rag_service.answer_question(
                question=message,
                top_k=top_k,
                user_id=user_id,
                workspace_id=session.workspace_id,
            )
            self.chat_repository.add_message(
                session_id=session_id,
                role="assistant",
                content=answer.answer,
                sources=answer.sources,
                metadata={"mode": mode.value},
            )
            yield {"type": "chunk", "content": answer.answer}
            yield {"type": "complete", "message": answer.answer, "sources": answer.sources}
            return

        history = self.chat_repository.list_messages(session_id=session_id)[-12:]
        ai_messages = [{"role": item.role, "content": item.content} for item in history]
        provider = AIProvider.GOOGLE if mode is ReasoningMode.THINK else AIProvider.AUTO
        response_text = ""

        async for chunk in self.ai_service.stream(
            ai_messages,
            mode=mode,
            provider=provider,
        ):
            response_text += chunk
            yield {"type": "chunk", "content": chunk}

        self.chat_repository.add_message(
            session_id=session_id,
            role="assistant",
            content=response_text,
            sources=None,
            metadata={"mode": mode.value},
        )
        yield {"type": "complete", "message": response_text, "sources": []}

