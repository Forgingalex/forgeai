"""Chat endpoints."""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.models.workspace import Workspace
from app.services.ai_service import stream_chat, ask_with_context
from app.services.rag_service import query_kb
import json

router = APIRouter()


class ChatMessageCreate(BaseModel):
    content: str
    session_id: Optional[int] = None
    workspace_id: Optional[int] = None
    use_rag: bool = False
    top_k: int = 3


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: Optional[List[str]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    id: int
    title: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None  # Can be None on creation (only set on update)
    
    class Config:
        from_attributes = True


@router.post("/sessions", response_model=ChatSessionResponse)
async def create_session(
    workspace_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session."""
    session = ChatSession(
        user_id=current_user.id,
        workspace_id=workspace_id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_sessions(
    workspace_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's chat sessions."""
    query = db.query(ChatSession).filter(ChatSession.user_id == current_user.id)
    if workspace_id:
        query = query.filter(ChatSession.workspace_id == workspace_id)
    sessions = query.order_by(ChatSession.updated_at.desc()).all()
    return sessions


@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a session."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.messages


@router.websocket("/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: int
):
    """WebSocket endpoint for streaming chat with authentication."""
    await websocket.accept()
    
    # Get database session (WebSocket can't use Depends)
    from app.core.database import SessionLocal
    from app.core.security import decode_access_token
    db = SessionLocal()
    
    try:
        # Get token from query params
        query_params = dict(websocket.query_params)
        token = query_params.get("token")
        
        # Authenticate user via token (from query params or first message)
        username = None
        if token:
            try:
                payload = decode_access_token(token)
                username = payload.get("sub")  # Token contains username, not user_id
            except:
                pass
        
        # Get session and verify ownership
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            await websocket.close(code=1008, reason="Session not found")
            db.close()
            return
        
        # Verify user owns session if token provided
        if username:
            # Look up user by username and verify session ownership
            user = db.query(User).filter(User.username == username).first()
            if not user or session.user_id != user.id:
                await websocket.close(code=1008, reason="Unauthorized")
                db.close()
                return
        
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle auth token in first message if not in query
            if not username and "token" in message_data:
                try:
                    payload = decode_access_token(message_data["token"])
                    username = payload.get("sub")
                    # Look up user by username and verify session ownership
                    user = db.query(User).filter(User.username == username).first()
                    if not user or session.user_id != user.id:
                        await websocket.close(code=1008, reason="Unauthorized")
                        db.close()
                        return
                except:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Invalid token"
                    }))
                    continue
            
            user_message = message_data.get("message", "")
            use_rag = message_data.get("use_rag", False)
            top_k = message_data.get("top_k", 3)
            
            if not user_message:
                continue
            
            # Save user message
            user_msg = ChatMessage(
                session_id=session_id,
                role="user",
                content=user_message,
            )
            db.add(user_msg)
            db.commit()
            
            # Get conversation history
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.created_at).all()
            
            # Prepare messages for AI
            ai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages[-10:]  # Last 10 messages for context
            ]
            
            # Get response
            if use_rag:
                # Use RAG
                try:
                    response_text = ask_with_context(user_message, top_k=top_k)
                    # Extract sources from response
                    sources = []
                    if "Sources used:" in response_text:
                        parts = response_text.split("Sources used:")
                        response_text = parts[0].strip()
                        sources_str = parts[1].strip() if len(parts) > 1 else ""
                        sources = [s.strip() for s in sources_str.split(",") if s.strip()]
                except Exception as e:
                    response_text = f"Error in RAG: {str(e)}"
                    sources = []
            else:
                # Regular chat - auto mode (tries Google first, falls back to Ollama)
                response_text = ""
                try:
                    async for chunk in stream_chat(ai_messages, provider="auto"):
                        response_text += chunk
                        await websocket.send_text(json.dumps({
                            "type": "chunk",
                            "content": chunk
                        }))
                except Exception as e:
                    response_text = f"Error: {str(e)}"
            
            # Save assistant message
            assistant_msg = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=response_text,
                sources=sources if use_rag else None,
            )
            db.add(assistant_msg)
            db.commit()
            
            # Send completion
            await websocket.send_text(json.dumps({
                "type": "complete",
                "message": response_text
            }))
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
    finally:
        db.close()

