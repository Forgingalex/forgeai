"""Workspace persistence repository."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.workspace import Workspace


class WorkspaceRepository:
    """Repository for knowledge workspaces."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, owner_id: int, name: str, description: Optional[str] = None) -> Workspace:
        """Create and persist a workspace."""
        workspace = Workspace(name=name, description=description, owner_id=owner_id)
        self.db.add(workspace)
        self.db.commit()
        self.db.refresh(workspace)
        return workspace

    def list_owned(self, owner_id: int) -> List[Workspace]:
        """Return workspaces owned by a user."""
        return (
            self.db.query(Workspace)
            .filter(Workspace.owner_id == owner_id)
            .order_by(Workspace.created_at.desc())
            .all()
        )

    def get_owned(self, workspace_id: int, owner_id: int) -> Optional[Workspace]:
        """Return a workspace only when owned by the user."""
        return (
            self.db.query(Workspace)
            .filter(Workspace.id == workspace_id, Workspace.owner_id == owner_id)
            .first()
        )

