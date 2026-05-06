"""Redis-backed WebSocket notifications."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def notification_channel(user_id: int) -> str:
    """Return the Redis channel used for a user's realtime events."""
    return f"forgeai:user:{user_id}:events"


def build_event(event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Build a standard notification payload."""
    return {
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }


def publish_user_event_sync(user_id: int, event_type: str, payload: Dict[str, Any]) -> None:
    """Publish a user notification from synchronous workers."""
    try:
        import redis
    except ImportError as exc:
        raise RuntimeError("redis package is required for notifications") from exc

    client = redis.Redis.from_url(settings.REDIS_URL)
    event = build_event(event_type, payload)
    client.publish(notification_channel(user_id), json.dumps(event))
    logger.info("notification_published", extra={"user_id": user_id, "type": event_type})


async def subscribe_user_events(user_id: int) -> AsyncGenerator[Dict[str, Any], None]:
    """Yield notifications for a user from Redis pub/sub."""
    try:
        import redis.asyncio as redis_async
    except ImportError as exc:
        raise RuntimeError("redis package is required for notifications") from exc

    client = redis_async.Redis.from_url(settings.REDIS_URL)
    pubsub = client.pubsub()
    await pubsub.subscribe(notification_channel(user_id))
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if not message:
                continue
            raw = message.get("data")
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            yield json.loads(raw)
    finally:
        await pubsub.unsubscribe(notification_channel(user_id))
        await pubsub.close()
        await client.close()

