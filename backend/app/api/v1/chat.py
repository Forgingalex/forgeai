"""Chat endpoints."""

from __future__ import annotations

import json
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.core.database import SessionLocal, get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.repositories.user_repository import UserRepository
from app.services.ai_service import ReasoningMode
from app.services.chat_service import ChatService

router = APIRouter()


class ChatSessionCreate(BaseModel):
    """Request body for creating a chat session."""

    workspace_id: Optional[int] = None


class ChatMessageCreate(BaseModel):
    """Request body for a non-streaming chat turn."""

    content: str
    session_id: Optional[int] = None
    workspace_id: Optional[int] = None
    mode: ReasoningMode = ReasoningMode.CHAT
    top_k: int = 5


class ChatMessageResponse(BaseModel):
    """Serialized chat message."""

    id: int
    role: str
    content: str
    sources: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    """Serialized chat session."""

    id: int
    title: Optional[str]
    workspace_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    payload: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new chat session."""
    service = ChatService(ChatRepository(db))
    return service.create_session(user_id=current_user.id, workspace_id=payload.workspace_id)


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_sessions(
    workspace_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's chat sessions."""
    service = ChatService(ChatRepository(db))
    return service.list_sessions(user_id=current_user.id, workspace_id=workspace_id)


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get messages for a chat session."""
    service = ChatService(ChatRepository(db))
    return service.list_messages(session_id=session_id, user_id=current_user.id)


@router.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: int) -> None:
    """WebSocket endpoint for streaming chat turns."""
    await websocket.accept()
    db = SessionLocal()

    try:
        token = websocket.cookies.get("access_token", "") or websocket.query_params.get("token", "")
        payload = decode_access_token(token) if token else {}
        username = payload.get("sub")
        user = UserRepository(db).get_by_username(str(username)) if username else None
        if not user:
            await websocket.close(code=1008, reason="Unauthorized")
            return

        service = ChatService(ChatRepository(db))
        if not service.chat_repository.get_owned_session(session_id=session_id, user_id=user.id):
            await websocket.close(code=1008, reason="Session not found")
            return

        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            message = str(data.get("message", "")).strip()
            if not message:
                continue

            mode = ReasoningMode(str(data.get("mode", ReasoningMode.CHAT.value)))
            top_k = int(data.get("top_k", 5))
            async for event in service.stream_turn(
                session_id=session_id,
                user_id=user.id,
                message=message,
                mode=mode,
                top_k=top_k,
            ):
                await websocket.send_text(json.dumps(event))
    except WebSocketDisconnect:
        return
    except Exception as exc:
        await websocket.send_text(json.dumps({"type": "error", "message": str(exc)}))
    finally:
        db.close()

