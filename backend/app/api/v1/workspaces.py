"""Workspace endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.auth import get_current_user
from app.models.user import User
from app.models.workspace import Workspace

router = APIRouter()


class WorkspaceCreate(BaseModel):
    name: str
    description: Optional[str] = None


class WorkspaceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


@router.post("/", response_model=WorkspaceResponse)
async def create_workspace(
    workspace: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workspace."""
    db_workspace = Workspace(
        name=workspace.name,
        description=workspace.description,
        owner_id=current_user.id,
    )
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)
    return db_workspace


@router.get("/", response_model=List[WorkspaceResponse])
async def get_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's workspaces."""
    workspaces = db.query(Workspace).filter(
        Workspace.owner_id == current_user.id
    ).order_by(Workspace.created_at.desc()).all()
    return workspaces


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific workspace."""
    workspace = db.query(Workspace).filter(
        Workspace.id == workspace_id,
        Workspace.owner_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    return workspace

