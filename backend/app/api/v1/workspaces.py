"""Workspace endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.v1.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.workspace_service import WorkspaceService

router = APIRouter()


class WorkspaceCreate(BaseModel):
    """Create workspace payload."""

    name: str
    description: Optional[str] = None


class WorkspaceResponse(BaseModel):
    """Serialized knowledge workspace."""

    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(
    workspace: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new workspace."""
    service = WorkspaceService(WorkspaceRepository(db))
    return service.create_workspace(
        owner_id=current_user.id,
        name=workspace.name,
        description=workspace.description,
    )


@router.get("/", response_model=List[WorkspaceResponse])
async def get_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the current user's workspaces."""
    service = WorkspaceService(WorkspaceRepository(db))
    return service.list_workspaces(owner_id=current_user.id)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a workspace by id."""
    service = WorkspaceService(WorkspaceRepository(db))
    return service.get_workspace(workspace_id=workspace_id, owner_id=current_user.id)

