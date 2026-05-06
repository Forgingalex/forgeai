"""Realtime notification endpoints."""

from __future__ import annotations

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.database import SessionLocal
from app.core.notifications import subscribe_user_events
from app.core.security import decode_access_token
from app.repositories.user_repository import UserRepository

router = APIRouter()


@router.websocket("/ws")
async def websocket_notifications(websocket: WebSocket) -> None:
    """Stream user-scoped background task notifications."""
    await websocket.accept()
    token = websocket.query_params.get("token", "")
    db = SessionLocal()
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        user = UserRepository(db).get_by_username(str(username))
        if not user:
            await websocket.close(code=1008, reason="Unauthorized")
            return

        async for event in subscribe_user_events(user.id):
            await websocket.send_text(json.dumps(event))
    except WebSocketDisconnect:
        return
    except Exception as exc:
        await websocket.send_text(json.dumps({"type": "error", "message": str(exc)}))
        await websocket.close(code=1011)
    finally:
        db.close()

