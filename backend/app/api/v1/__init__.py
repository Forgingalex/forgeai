from fastapi import APIRouter

from app.api.v1 import auth, chat, exams, files, flashcards, notifications, rag, study_planner, workspaces

"""API v1 routes."""

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["workspaces"])
api_router.include_router(flashcards.router, prefix="/flashcards", tags=["flashcards"])
api_router.include_router(exams.router, prefix="/exams", tags=["exams"])
api_router.include_router(rag.router, prefix="/rag", tags=["rag"])
api_router.include_router(study_planner.router, prefix="/study-planner", tags=["study-planner"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
