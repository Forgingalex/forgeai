"""Celery application for asynchronous ForgeAI work."""

from __future__ import annotations
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "forgeai",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.document_tasks"],
)

# Upstash requires 'rediss://' and specific SSL cert handling
if settings.CELERY_BROKER_URL.startswith("rediss://"):
    celery_app.conf.update(
        broker_use_ssl={"ssl_cert_reqs": "none"},
        redis_backend_use_ssl={"ssl_cert_reqs": "none"},
    )

celery_app.conf.update(
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    # connection retries on startup for cloud stability
    broker_connection_retry_on_startup=True,
)